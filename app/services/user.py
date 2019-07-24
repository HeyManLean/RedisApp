# -*- coding: utf-8 -*-
import time
from datetime import datetime

import config
from utils.string import get_random_str, get_hash_str
from app import redis_mapping
from app.const import (
    SESSION_USER_KEY, SESSION_TOKEN_KEY,
    SESSION_RECENT_ZKEY, USER_ID_COUNTER_KEY
)
from app.models.user import User
from app.services.common import Lock


def get_user(user_id: str):
    """获取用户"""
    user = User.load(user_id=user_id)
    return user


def create_user(username, pwd_md5, nickname):
    """创建新用户"""
    key = 'user:' + username
    with Lock(key) as lock:
        if not lock:
            return None

        user = User.load(username=username)
        if user:
            return None

        user_id = gen_user_id()
        now = datetime.now()

        user = User()
        user.user_id = user_id
        user.username = username
        user.nickname = nickname
        user.password = get_hash_str(pwd_md5, config.SECRET_KEY)
        user.login_time = user.create_time = user.update_time = now
        user.save_new()

        user_db = redis_mapping.get_db('session')
        user_db.hmset('user:%s' % user_id, {
            'user_id': user_id,
            'nickname': nickname,
            'followers': 0,
            'followings': 0,
            'posts': 0,
            'login': datetime.timestamp(now)
        })

    return user


def gen_user_id():
    """自增生成新的用户id"""
    redis_db = redis_mapping.get_db('counter')
    return int(redis_db.incr(USER_ID_COUNTER_KEY))


def validate_user(username: str, pwd_md5: str):
    """验证用户名和密码"""
    user = User.load(username=username)
    if not user:
        return None

    if not user.password == get_hash_str(pwd_md5, config.SECRET_KEY):
        return None

    return user


def login_user(user: User):
    """用户登录"""
    redis_db = redis_mapping.get_db('session')
    user.login_time = datetime.now()
    user.update()

    token = get_random_str()
    pipeline = redis_db.pipeline()
    user_key = SESSION_USER_KEY.format(token=token)
    pipeline.set(user_key, user.user_id, ex=config.SESSION_EXPIRE_TIME)

    token_key = SESSION_TOKEN_KEY.format(user_id=user.user_id)
    pipeline.set(token_key, token, ex=config.SESSION_EXPIRE_TIME)

    pipeline.zadd(SESSION_RECENT_ZKEY, {user.user_id: int(time.time())})

    # 清理登录状态，可以单独起一个程序清理，否则每秒执行次数太多
    pipeline.zremrangebyrank(SESSION_RECENT_ZKEY, 0, -1000)

    pipeline.execute()
    return token


def logout_user(token: str):
    """用户注销"""
    key = 'user:logout:' + token
    with Lock(key) as lock:
        if not lock:
            return False

        redis_db = redis_mapping.get_db('session')
        user_key = SESSION_USER_KEY.format(token=token)
        user_id = redis_db.get(user_key)
        if not user_id:
            return False

        token_key = SESSION_TOKEN_KEY.format(user_id=user_id)

        pipeline = redis_db.pipeline()
        pipeline.delete(user_key)
        pipeline.delete(token_key)
        pipeline.execute()

    return True


def check_token(token: str):
    """检查登录状态"""
    redis_db = redis_mapping.get_db('session')
    user_key = SESSION_USER_KEY.format(token=token)
    return int(redis_db.get(user_key) or 0)
