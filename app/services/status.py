# -*- coding: utf-8 -*-
"""
消息状态
"""
import time
import json
from datetime import datetime
import random

from app import redis_mapping
from app.const import (
    STATUS_ID_COUNTER_KEY, STATUS_HOME_TIMELINE_SIZE,
    POST_PER_PASS
)
from app.models.user import User
from app.models.status import Status, PublishStatus
from app.services.common import Lock


def gen_status_id():
    """自增生成新的用户id"""
    redis_db = redis_mapping.get_db('counter')
    return int(redis_db.incr(STATUS_ID_COUNTER_KEY))


def create_status(content, user_id):
    user = User.load(user_id=user_id)
    if not user:
        return None

    status_id = gen_status_id()
    now = datetime.now()

    status = Status()
    status.status_id = status_id
    status.content = content
    status.user_id = user_id
    status.nickname = user.nickname

    status.create_time = now
    status.publish_status = PublishStatus.INIT.value

    status.save_new()

    status_db = redis_mapping.get_db('status')
    status_db.publish('streaming:status:', json.dumps(status.to_json()))

    user_db = redis_mapping.get_db('session')
    user_db.hincrby('user:%s' % user_id, 'posts')

    # 处理 redis 记录

    return status


def get_status_contents(user_id, timeline='home', page=1, count=30):
    """获取时间线的状态消息列表"""
    redis_db = redis_mapping.get_db('status')
    pipeline = redis_db.pipeline()
    pipeline.zrevrange(
        '%s:%s' % (timeline, user_id), (page - 1) * count, page * count - 1
    )
    pipeline.zcount('%s:%s' % (timeline, user_id), 0, 'inf')
    statuses, total = pipeline.execute()[-2:]
    statuses = list(map(int, statuses))

    query_dict = {'status_id': {'$in': statuses}}
    sort = ['-create_time']
    items = []
    for status in Status.query(query_dict, sort):
        items.append({
            'status_id': status['status_id'],
            'content': status['content'],
            'user_id': status['user_id'],
            'create_time': status['create_time']
        })

    return {
        'total': total,
        'items': items,
        'page': page,
        'count': count
    }


def follow_user(uid, other_uid):
    redis_db = redis_mapping.get_db('status')
    fkey1 = 'followings:%s' % uid
    fkey2 = 'followers:%s' % other_uid

    if redis_db.zscore(fkey1, other_uid):
        return False

    now = int(time.time())

    pipeline = redis_db.pipeline()
    pipeline.zadd(fkey1, {other_uid: now})
    pipeline.zadd(fkey2, {uid: now})
    pipeline.zrevrange(
        'profile:%s' % other_uid, 0,
        STATUS_HOME_TIMELINE_SIZE - 1, withscores=True)

    followings, followers, status_and_score = pipeline.execute()[-3:]

    if status_and_score:
        pipeline.zadd('home:%s' % uid, dict(status_and_score))
    pipeline.zremrangebyrank('home:%s' % uid, 0, -STATUS_HOME_TIMELINE_SIZE - 1)
    pipeline.execute()

    user_db = redis_mapping.get_db('session')
    pipeline = user_db.pipeline()
    pipeline.hincrby('user:%s' % uid, 'followings', int(followings))
    pipeline.hincrby('user:%s' % other_uid, 'followers', int(followers))
    pipeline.execute()

    return True


def unfollow_user(uid, other_uid):
    redis_db = redis_mapping.get_db('status')
    fkey1 = 'followings:%s' % uid
    fkey2 = 'followers:%s' % other_uid

    if not redis_db.zscore(fkey1, other_uid):
        return False

    pipeline = redis_db.pipeline()
    pipeline.zrem(fkey1, other_uid)
    pipeline.zrem(fkey2, uid)
    pipeline.zrevrange(
        'profile:%s' % other_uid, 0, STATUS_HOME_TIMELINE_SIZE - 1)
    followings, followers, status = pipeline.execute()[-3:]

    if status:
        pipeline.zrem('home:%s' % uid, *status)
    pipeline.execute()

    user_db = redis_mapping.get_db('session')
    pipeline = user_db.pipeline()
    pipeline.hincrby('user:%s' % uid, 'followings', - abs(followings))
    pipeline.hincrby('user:%s' % other_uid, 'followers', - abs(followers))
    pipeline.execute()

    return True


def post_status(uid, content, **data):
    status = create_status(content, uid)
    if not status:
        return None

    now = datetime.timestamp(status.create_time)

    redis_db = redis_mapping.get_db('status')
    pipeline = redis_db.pipeline()
    pipeline.zadd('profile:%s' % uid, {status.status_id: now})

    syndicate_status(uid, status.status_id, now)

    return True


def syndicate_status(uid, status_id, timestamp, start=0):
    redis_db = redis_mapping.get_db('status')
    followers = redis_db.zrangebyscore(
        'followers:%s' % uid, start, 'inf', start=0, num=POST_PER_PASS)

    pipeline = redis_db.pipeline()

    for follower in followers:
        pipeline.zadd('home:' + follower, {status_id: timestamp})
        pipeline.zremrangebyrank(
            'home:' + follower, 0, -STATUS_HOME_TIMELINE_SIZE - 1)
    pipeline.execute()

    # 自己的主页
    pipeline.zadd('home:%s' % uid, {status_id: timestamp})
    pipeline.zremrangebyrank('home:%s' % uid, 0, -STATUS_HOME_TIMELINE_SIZE - 1)
    pipeline.execute()

    # TODO 延迟同步

    return True


def delete_status(uid, status_id):
    key = 'status:%s' % status_id
    with Lock(key) as lock:
        if not lock:
            return False

        status = Status.load(status_id=status_id)
        if not status or status.user_id != uid:
            return False

        status_db = redis_mapping.get_db('status')
        pipeline = status_db.pipeline()

        data = status.to_json()
        data['deleted'] = True
        pipeline.publish('streaming:status:', json.dump(data))

        pipeline.zrem('profile:%s' % uid, status_id)
        pipeline.zrem('home:%s' % uid, status_id)
        pipeline.execute()

        user_db = redis_mapping.get_db('session')
        user_db.hincrby('user:%s' % uid, 'posts', -1)

        Status.remove_one({'status_id': status_id})
    return True


def filter_content(user_id, filter_type, arg, quit):
    """过滤内容，推荐内容"""
    redis_db = redis_mapping.get_db('status')
    match = create_filters(user_id, filter_type, arg)

    pubsub = redis_db.pubsub()
    pubsub.subscribe(['streaming:status:'])

    for item in pubsub.listen():
        message = item['data']
        decoded = json.loads(message)

        if match(decoded):
            if decoded.get('deleted'):
                yield json.dumps({
                    'status_id': decoded['status_id'],
                    'deleted': True
                })

            else:
                yield message

        if quit[0]:
            break

        pubsub.reset()


def create_filters(user_id, filter_type, arg):
    if filter_type == 'sample':
        return SampleFilter(user_id, arg)
    elif filter_type == 'track':
        return TrackFilter(arg)
    elif filter_type == 'follow':
        return FollowFilter(arg)
    elif filter_type == 'location':
        return LocationFilter(arg)

    raise Exception('Unknown filter')


def SampleFilter(uid, percent):
    percent = percent or 10
    ids = list(range(100))
    shuffler = random.Random(uid)
    shuffler.shuffle(ids)
    keep = set(ids[:max(percent, 1)])

    def check(status):
        return (status['status_id'] % 100) in keep

    return check


def TrackFilter(list_of_strings):
    groups = []
    for group in list_of_strings:
        group = set(group.lower().split())
        if group:
            groups.append(group)

    def check(status):
        message_words = set(status['content'].lower().split())
        for group in groups:
            if len(group & message_words) == len(group):
                return True

        return False
    return check


def FollowFilter(names):
    nset = set()
    for name in names:
        nset.add('@' + name.lower().lstrip('@'))

    def check(status):
        message_words = set(status['content'].lower().split())
        message_words.add('@' + status['nickname'].lower())

        return message_words & nset

    return check


def LocationFilter(list_of_boxes):
    boxes = []
    for start in range(0, len(list_of_boxes) - 3, 4):
        boxes.append(
            list(map(float, list_of_boxes[start:start + 4]))
        )

    def check(status):
        location = status.get('location')
        if not location:
            return False

        lat, lon = list(map(float, location.split(',')))
        for box in boxes:
            if (box[1] <= lat <= box[3] and
                box[0] < lon <= box[2]):
                return True

        return False

    return check
