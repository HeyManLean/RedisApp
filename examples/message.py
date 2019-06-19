#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
消息拉取
"""
import time
import json

from redis import Redis

from lock import acquire_lock
from lock import release_lock


db = Redis(decode_responses=True)


def create_chat(sender, recipients, message, chat_id=None):
    chat_id = chat_id or str(db.incr('ids:chat'))

    recipients.append(sender)
    recipientsd = dict((r, 0) for r in recipients)

    pipeline = db.pipeline()
    pipeline.zadd('chat:' + chat_id, **recipientsd)
    for rec in recipients:
        pipeline.zadd('seen:' + rec, chat_id, 0)
    pipeline.execute()

    return send_message(chat_id, sender, message)


def send_message(chat_id, sender, message):
    identifier = acquire_lock('chat:' + chat_id)
    if not identifier:
        raise Exception("Couldn't get the lock")
    try:
        mid = db.incr('ids:' + chat_id)
        ts = time.time()
        packed = json.dumps({
            'id': mid,
            'ts': ts,
            'sender': sender,
            'message': message
        })
        db.zadd('msgs:' + chat_id, packed, mid)
    finally:
        release_lock('chat:' + chat_id, identifier)


def fetch_pending_message(recipient):
    seen = db.zrange('seen:' + recipient, 0, -1, withscores=True)

    pipeline = db.pipeline()
    for chat_id, seen_id in seen:
        pipeline.zrangebyscore('msgs:' + chat_id, seen_id + 1, 'inf')
    # chat_id, seen_id, unseen_msgs
    chat_info = zip(seen, pipeline.execute())

    for i, ((chat_id, seen_id), messages) in enumerate(chat_info):
        if not messages:
            continue

        messages[:] = map(json.loads, messages)
        seen_id = messages[-1]['id']
        db.zadd('chat:' + chat_id, recipient, seen_id)
        pipeline.zadd('seen:' + recipient, chat_id, seen_id)

        # 把所有人都已经读过的消息都删除, 消息meta信息都是存到其他永久保存的数据的
        min_id = db.zrange('chat:' + chat_id, 0, 0, withscores=True)
        if min_id:
            pipeline.zremrangebyscore('msgs:' + chat_id, 0, min_id[0][1])

        chat_info[i] = (chat_id, messages)
    pipeline.execute()

    return chat_info


def join_chat(chat_id, user):
    message_id = int(db.get('ids:' + chat_id))

    pipeline = db.pipeline()
    pipeline.zadd('chat:' + chat_id, user, message_id)
    pipeline.zadd('seen:' + user, chat_id, message_id)
    pipeline.execute()


def leave_chat(chat_id, user):
    pipeline = db.pipeline()
    pipeline.zrem('chat:' + chat_id, user)
    pipeline.zrem('seen:' + user, chat_id)
    pipeline.zcard('chat:' + chat_id)

    if not pipeline.execute()[-1]:
        pipeline.delete('msgs:' + chat_id)
        pipeline.delete('ids:' + chat_id)
        pipeline.execute()
    else:
        oldest = db.zrange('chat:' + chat_id, 0, 0, withscores=True)
        db.zremrangebyscore('msgs:' + chat_id, 0, oldest[0][1])
