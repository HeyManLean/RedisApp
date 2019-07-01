# -*- coding: utf-8 -*-
import time
from datetime import datetime
from functools import wraps

from utils.string import get_random_str, get_hash_str
from utils.db import acquire_lock_with_timeout, release_lock
from app import redis_db
from app.models.user import User
from app.const import (
    SESSION_USER_KEY, SESSION_TOKEN_KEY,
    SESSION_RECENT_ZKEY, USER_ID_COUNTER_KEY,
    SESSION_KEY_EXPIRES
)


def get_user(user_id: str):
    """获取用户"""
    user = User.load(user_id=user_id)
    return user


def create_user(username, pwd_md5):
    """创建新用户"""
    now = datetime.now()

    user = User()
    user.user_id = gen_user_id()
    user.username = username
    user.password = get_hash_str(pwd_md5)
    user.login_time = user.create_time = user.update_time = now

    user.save_new()
    return user


def gen_user_id():
    """自增生成新的用户id"""
    return int(redis_db.incr(USER_ID_COUNTER_KEY))


def login_user(username: str, pwd_md5: str):
    """用户登录"""
    user = User.load(username=username)
    if not user:
        user = create_user(username, pwd_md5)
    else:
        user.login_time = datetime.now()
        user.update()

    pipeline = redis_db.pipeline()
    token = get_random_str()
    user_key = SESSION_USER_KEY.format(token=token)
    pipeline.set(user_key, user.user_id, ex=SESSION_KEY_EXPIRES)

    token_key = SESSION_TOKEN_KEY.format(user_id=user.user_id)
    pipeline.set(token_key, token, ex=SESSION_KEY_EXPIRES)

    pipeline.zadd(SESSION_RECENT_ZKEY, user.user_id, int(time.time()))
    pipeline.zremrangebyrank(SESSION_RECENT_ZKEY, 0, -1000)

    pipeline.execute()
    return user


def logout_user(token: str):
    """用户注销"""
    lockname = 'user:logout:' + token
    lock = acquire_lock_with_timeout(redis_db, lockname, 1)
    if not lock:
        return False

    user_key = SESSION_TOKEN_KEY.format(token=token)
    user_id = redis_db.get(user_key)
    if not user_id:
        return False

    token_key = SESSION_TOKEN_KEY.format(user_id=user_id)

    pipeline = redis_db.pipeline()
    pipeline.delete(user_id)
    pipeline.delete(token_key)
    pipeline.execute()

    release_lock(redis_db, lockname, lock)

    return True


def check_token(token: str):
    """检查登录状态"""
    user_key = SESSION_TOKEN_KEY.format(token=token)
    return redis_db.get(user_key)
