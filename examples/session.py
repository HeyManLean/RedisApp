# -*- coding: utf-8 -*-
import time
import json

from app import redis_db


def check_token(token):
    return redis_db.hget('login:', token)


def update_token(token, user, item=None):
    timestamp = time.time()
    # token 记录用户信息
    redis_db.hset('login:', token, user)

    # 按登录时间排序最近登录用户token, 清理时间过久的
    redis_db.zadd('recent:', token, timestamp)

    if item:
        redis_db.zadd('viewed:' + token, item, timestamp)
        # 只保留用户浏览的最后 25 个商品
        redis_db.zremrangebyrank('viewed:' + token, 0, -26)
        # 对于浏览的商品按浏览次数排序
        redis_db.zincrby('viewed:', item, -1)  # 往索引 0 爬


def add_to_cart(token, item, count):
    if count <= 0:
        redis_db.hdel('cart:' + token, item)
    else:
        redis_db.hset('cart:' + token, item, count)


QUIT = False
LIMIT = 10000000


def clean_sessions():
    while not QUIT:
        size = redis_db.zcard('recent:')
        if size <= LIMIT:
            time.sleep(1)
            continue
        
        end_index = min(size - LIMIT, 100)
        tokens = redis_db.zrange('recent:', 0, end_index - 1)

        session_keys = []
        for token in tokens:
            session_keys.append('viewed:' + token)
            session_keys.append('cart:' + token)
        
        redis_db.delete(*session_keys)
        redis_db.hdel('login:', *token)
        redis_db.zrem('recent:', *token)



def schedule_row_cache(row_id, delay):
    """计划缓存数据行
    Args:
        row_id (str): 'users:1:posts:1', 资源唯一id
        delay (int): 10, 更新时间间隔
    """
    redis_db.zadd('delay:', row_id, delay)  # 数据行更新时间延迟
    redis_db.zadd('schedule:', row_id, time.time())  # 数据行更新时间点


def cache_rows():
    while not QUIT:
        next = redis_db.zrange('schedule:', 0, 0, withscores=True)
        now = time.time()
        if not next or next[0][1] > now:
            time.sleep(.05)
            continue
        
        row_id = next[0][0]

        # 延迟为 0 视为删除
        delay = redis_db.zscore('delay:', row_id)
        if delay <= 0:
            redis_db.zrem('delay:', row_id)
            redis_db.zrem('schedule:', row_id)
            redis_db.delete('inv:' + row_id)
            continue
        
        row = Inventory.get(row_id)
        redis_db.zadd('schedule:', row_id, now + delay)
        redis_db.set('inv:' + row_id, json.dumps(row.to_dict()))


class Inventory(object):  # db.Model
    pass


def rescale_viewed():
    while not QUIT:
        # 删除 20000 名之后的商品
        redis_db.zremrangebyrank('viewed:', 0, -20001)
        # 浏览次数减半
        redis_db.zinterstore('viewed:', {'viewed:': .5})
        time.sleep(300)


def can_cache(request):
    item_id = extract_item_id(request)
    if not item_id or is_dynamic(request):
        return False
    rank = redis_db.zrank('viewed:', item_id)
    return rank is not None and rank < 10000


def extract_item_id(request):
    return request.item_id


def is_dynamic(request):
    return request.is_dynamic
