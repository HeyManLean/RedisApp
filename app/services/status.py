# -*- coding: utf-8 -*-
"""
消息状态
"""
import time
from datetime import datetime

from app import redis_mapping
from app.const import STATUS_ID_COUNTER_KEY, STATUS_HOME_TIMELINE_SIZE
from app.models.user import User
from app.models.status import Status, PublishStatus


def gen_status_id():
    """自增生成新的用户id"""
    redis_db = redis_mapping.get_db('counter')
    return int(redis_db.incr(STATUS_ID_COUNTER_KEY))


def create_status(content, user_id):
    user = User.load(user_id=user_id)

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

    user_db = redis_mapping.get_db('user')
    user_db.incr('user:' + user_id, 'posts')

    # 处理 redis 记录

    return status


def get_status_contents(user_id, timeline='home:', page=1, count=30):
    """获取时间线的状态消息列表"""
    redis_db = redis_mapping.get_db('status')
    statuses = redis_db.zrevrange(
        '%s%s' % (timeline, user_id), (page - 1) * count, page * count - 1
    )
    query_dict = {'status_id': {'$in': statuses}}
    sort = [('create_time', -1)]
    result = []
    for status in Status.query(query_dict, sort):
        result.append({
            'status_id': status['status_id'],
            'content': status['content'],
            'user_id': user_id,
            'nickname': status['nickname'],
            'create_time': status['create_time']
        })

    return result


def follow_user(uid, other_uid):
    redis_db = redis_mapping.get_db('status')
    fkey1 = 'followings:' + uid
    fkey2 = 'followers:' + other_uid

    if redis_db.zscore(fkey1, other_uid):
        return False

    now = int(time.time())

    pipeline = redis_db.pipeline()
    pipeline.zadd(fkey1, other_uid, now)
    pipeline.zadd(fkey2, uid, now)
    pipeline.zrevrange(
        'profile:' + other_uid, 0,
        STATUS_HOME_TIMELINE_SIZE - 1, withscores=True)

    followings, followers, status_and_score = pipeline.execute()[-3:]

    if status_and_score:
        pipeline.zadd('home:' + uid, **dict(status_and_score))
    pipeline.zremrangebyrank('home:' + uid, 0, -STATUS_HOME_TIMELINE_SIZE - 1)
    pipeline.execute()

    user_db = redis_mapping.get_db('user')
    pipeline = user_db.pipeline()
    pipeline.incr('user:' + uid, 'followings', int(followings))
    pipeline.incr('user:' + other_uid, 'followers', int(followers))
    pipeline.execute()

    return True


def unfollow_user(uid, other_uid):
    redis_db = redis_mapping.get_db('status')
    fkey1 = 'followings:' + uid
    fkey2 = 'followers:' + other_uid

    if not redis_db.zscore(fkey1, other_uid):
        return False

    pipeline = redis_db.pipeline()
    pipeline.zrem(fkey1, other_uid)
    pipeline.zrem(fkey2, uid)
    pipeline.zrevrange('profile:' + other_uid, 0, STATUS_HOME_TIMELINE_SIZE - 1)
    followings, followers, status = pipeline.execute()[-3:]

    if status:
        pipeline.zrem('home:' + uid, **status)
    pipeline.execute()

    user_db = redis_mapping.get_db('user')
    pipeline = user_db.pipeline()
    pipeline.incr('user:' + uid, 'followings', - int(followings))
    pipeline.incr('user:' + other_uid, 'followers', - int(followers))
    pipeline.execute()

    return True


def post_status(uid, content, **data):
    status = create_status(content, uid)

    fer_key = 'followers:' + uid
    now = datetime.timestamp(status.create_time)

    redis_db = redis_mapping.get_db('status')
    pipeline = redis_db.pipeline()
    pipeline.zadd('profile:' + uid, **{status.status_id: now})
    pipeline.zadd('home:' + uid, **{status.status_id: now})
    pipeline.zremrangebyrank('home:' + uid, 0, -STATUS_HOME_TIMELINE_SIZE - 1)

    pipeline.zrange(fer_key, 0, -1)
    followers = pipeline.execute()[-1] or []

    for other_uid in followers:
        pipeline.zadd('home:' + other_uid, status.status_id, now)
        pipeline.zremrangebyrank(
            'home:' + other_uid, 0, -STATUS_HOME_TIMELINE_SIZE - 1)

    pipeline.execute()
    return True


def syndicate_status(uid, post, start=0):
    pass


def delete_status(uid, status_id):
    Status.remove_one({'status_id': status_id})
    user_db = redis_mapping.get_db('user')
    user_db.incr('user:' + uid, 'posts', -1)
    return True
