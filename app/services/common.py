# -*- coding: utf-8 -*-
"""
一些通用的方法
"""
from functools import wraps
from utils.db import acquire_lock_with_timeout, release_lock
from app import redis_mapping


class Lock(object):
    def __init__(self, key, timeout=10):
        self.db = redis_mapping.get_db('lock')
        self.timeout = timeout
        self.key = key
        self.lock = None

    def __enter__(self):
        self.lock = acquire_lock_with_timeout(
            self.db, self.key, lock_timeout=self.timeout)
        return self.lock

    def __exit__(self, exc_type, exc_value, exc_traceback):
        release_lock(self.db, self.key, self.lock)


def cache(timeout=60):
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            pass

        return new_func
    return decorator
