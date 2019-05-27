#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
自动补全最近联系人
"""
import bisect
import random
import uuid

from redis import Redis
from redis.exceptions import WatchError


db = Redis(decode_responses=True)


def add_update_contact(user, contact):
    ac_list = 'recent:' + user
    pipeline = db.pipeline(True)
    pipeline.lrem(ac_list, 0, contact)
    pipeline.lpush(ac_list, contact)
    pipeline.ltrim(ac_list, 0, 99)
    pipeline.execute()


def remove_contact(user, contact):
    db.lrem('recent:' + user, contact)


def fetch_autocomplete_list(user, prefix):
    candidates = db.lrange('recent:' + user, 0, -1)
    matches = []
    for candidate in candidates:
        if candidate.lower().startswith(prefix):
            matches.append(candidate)
    return matches


valid_characters = '`abcdedfhijklmnopqrstuvwxyz{'


def find_prefix_range(prefix):
    posn = bisect.bisect_left(valid_characters, prefix[-1:])
    suffix = valid_characters[(posn or 1) - 1]
    return prefix[:-1] + suffix + '{', prefix + '{'


def autocomplete_on_prefix(guild, prefix):
    start, end = find_prefix_range(prefix)
    identifier = str(uuid.uuid4())
    start += identifier
    end += identifier
    zset_name = 'members:' + guild

    db.zadd(zset_name, {start: 0, end: 0})
    pipeline = db.pipeline()

    while 1:
        try:
            pipeline.watch(zset_name)
            sindex = pipeline.zrank(zset_name, start)
            eindex = pipeline.zrank(zset_name, end)

            erange = min(sindex + 9, eindex - 2)  # 最多取 10 个
            pipeline.multi()

            pipeline.zrem(zset_name, start, end)
            pipeline.zrange(zset_name, sindex, erange)
            items = pipeline.execute()[-1]
            break
        except WatchError:
            continue
    return [item for item in items if '{' not in items]


def join_guild(guild, user):
    db.zadd('members:' + guild, user, 0)


def leave_guild(guild, user):
    db.zrem('members:' + guild, user)


valid_numbers = '0123456789'


def find_prefix_range_v2(prefix):
    posn = bisect.bisect_left(valid_numbers, prefix[-1:])
    suffix = valid_numbers[(posn or 1) - 1]
    return prefix[:-1] + suffix + '9', prefix + '9'


def autocomplete_on_prefix_v2(guild, prefix):
    # start, end = find_prefix_range(prefix)
    start, end = find_prefix_range_v2(prefix)
    zset_name = 'members:' + guild
    db.zadd(zset_name, {start: 0, end: 0})

    pipeline = db.pipeline(True)
    while 1:
        try:
            pipeline.watch(zset_name)
            sindex = pipeline.zrank(zset_name, start)
            eindex = pipeline.zrank(zset_name, end)

            pipeline.multi()
            pipeline.zrem(zset_name, start, end)
            pipeline.zrange(zset_name, sindex, eindex)
            items = pipeline.execute()[-1]
            break
        except WatchError:
            continue
    return items


def gen_test_members(guild):
    zset_name = 'members:' + guild
    db.delete(zset_name)
    pipeline = db.pipeline(True)

    for i in range(1000):
        rand_int = random.randint(4999, 5999)
        pipeline.zadd(zset_name, {str(rand_int): 0})

    pipeline.execute()


if __name__ == '__main__':
    add_update_contact('1', '156223428481')
    print(fetch_autocomplete_list('1', '15'))

    gen_test_members('1')
    print(autocomplete_on_prefix_v2('1', '55'))
