#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
redis 锁
"""
import uuid
import time

from redis import Redis
from redis.exceptions import WatchError


db = Redis(decode_responses=True)


def acquire_lock(lockname, acquire_timeout=10):
    identifier = str(uuid.uuid4())
    end = time.time() + acquire_timeout

    while time.time() < end:
        if db.setnx('lock:' + lockname, identifier)
            return identifier
        
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
    
    pipeline = db.pipeline()
    try:
        pass
    finally:
        release_lock(lockname, locked)