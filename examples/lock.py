#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
redis 锁
"""
import uuid
import time
import math

from redis import Redis
from redis.exceptions import WatchError


db = Redis(decode_responses=True)


def acquire_lock(lockname, acquire_timeout=10):
    identifier = str(uuid.uuid4())
    end = time.time() + acquire_timeout

    while time.time() < end:
        if db.setnx('lock:' + lockname, identifier):
            return identifier

        time.sleep(.001)
    return False


def acquire_lock_with_timeout(lockname, acquire_timeout=10, lock_timeout=10):
    identifier = str(uuid.uuid4())
    lock_timeout = int(math.ceil(lock_timeout))
    lockname = 'lock:' + lockname

    end = time.time() + acquire_timeout
    while time.time() < end:
        if db.setnx(lockname, identifier):
            db.expire(lockname, lock_timeout)
            return identifier
        elif db.ttl(lockname) <= 0:
            db.expire(lockname, lock_timeout)

        time.sleep(.001)
    return False


def release_lock(lockname, identifier):
    pipe = db.pipeline()
    lockname = 'lock:' + lockname

    while 1:
        try:
            pipe.watch(lockname)
            if pipe.get(lockname) == identifier:
                pipe.multi()
                pipe.delete(lockname)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except WatchError:
            pass
    return False


def purchase_item_with_lock(itemid):
    lockname = 'item:' + itemid
    locked = acquire_lock(lockname)
    if not locked:
        return False

    try:
        pass
    finally:
        release_lock(lockname, locked)


# ------- 信号量 -------
def acquire_semaphore(semname, limit, timeout=10):
    identifier = str(uuid.uuid4())
    now = time.time()

    pipeline = db.pipeline()
    pipeline.zremrangebyscore(semname, '-inf', now - timeout)
    pipeline.zadd(semname, identifier, now)
    pipeline.zrank(semname, identifier)
    if pipeline.execute()[-1] < limit:
        return identifier

    db.zrem(semname, identifier)
    return None


def release_semaphore(semname, identifier):
    db.zrem(semname, identifier)


def acquire_fair_semaphore(semname, limit, timeout=10):
    identifier = str(uuid.uuid4())
    now = time.time()
    czset = semname + ':owner'
    ctr = semname + ':counter'

    pipeline = db.pipeline()
    pipeline.zremrangebyscore(semname, '-inf', now - timeout)
    pipeline.zinterstore(czset, {czset: 1, semname: 0})

    pipeline.incr(ctr)

    counter = pipeline.execute()[-1]

    pipeline.zadd(semname, identifier, now)
    pipeline.zadd(czset, identifier, counter)

    pipeline.zrank(czset, identifier)
    if pipeline.execute()[-1] < limit:
        return identifier

    pipeline.zrem(semname, identifier)
    pipeline.zrem(czset, identifier)
    pipeline.execute()
    return None


def release_fair_semephore(semname, identifier):
    pipeline = db.pipeline()
    pipeline.zrem(semname, identifier)
    pipeline.zrem(semname + ':owner', identifier)
    return pipeline.execute()[0]


def refresh_fair_semephore(semname, identifier):
    if db.zadd(semname, identifier, time.time()):  # 如果不存在的话, zadd 返回 1
        refresh_fair_semephore(semname, identifier)
        return False
    return True


def acquire_semaphore_with_lock(semname, limit, timeout=10):
    identifier = acquire_lock(semname)
    if identifier:
        try:
            return acquire_fair_semaphore(semname, limit, timeout)
        finally:
            release_lock(semname, identifier)


if __name__ == '__main__':
    db.expire('aaaaaa', 3)
    time.sleep(3)
    print(db.ttl('aaaaaa'))
