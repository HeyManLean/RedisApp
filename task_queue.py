#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
队列
"""
import time
import json
import uuid

from redis import Redis

from lock import acquire_lock
from lock import release_lock


db = Redis(decode_responses=True)


QUIT = True

log_error = log_success = print


def fetch_data_and_send_sold_email(data):
    pass


def send_sold_email_via_queue(seller, item, price, buyer):
    data = {
        'seller_id': seller,
        'item_id': item,
        'price': price,
        'buyer_id': buyer,
        'time': time.time()
    }
    db.rpush('queue:email', json.dumps(data))


def process_sold_email_queue():
    while not QUIT:
        packed = db.blpop(['queue:email'], timeout=30)
        if not packed:
            continue

        to_send = json.loads(packed[1])
        try:
            fetch_data_and_send_sold_email(to_send)
        except Exception as e:
            log_error('Failed to send sold email', e, to_send)
        else:
            log_success('Sent sold email', to_send)


def worker_watch_queue(queue, callbacks):
    """多任务处理 -- queue 放了不同的任务 (发邮件, 统计)数据"""
    while not QUIT:
        packed = db.blpop([queue], timeout=30)
        if not packed:
            continue

        # 队列的数据格式: [task_name, (args1, args2, ...)]
        name, args = json.loads(packed[1])
        if name not in callbacks:
            log_error('Unknown callback %s' % name)
            continue
        callbacks[name](*args)


def worker_watch_queues(queues, callbacks):
    """优先级任务 queues 是有序列表"""
    while not QUIT:
        packed = db.blpop(queues, timeout=30)
        if not packed:
            continue

        name, args = json.loads(packed[1])
        if name not in callbacks:
            log_error('Unknown callback %s' % name)
            continue
        callbacks[name](*args)


# 延时执行
def execute_later(queue, name, args, delay=0):
    identifier = str(uuid.uuid4())
    item = json.dumps([identifier, queue, name, args])
    if delay > 0:
        db.zadd('delayed:', item, time.time() + delay)
    else:
        # 立即执行, 需要启动一个 worker_watch_queues 程序
        # 解析 [identifier, queue, name, args] 结构
        db.rpush('queue:' + queue, item)
    return identifier


def poll_queue():
    """拉取到时间执行的任务, 交到 worker_watch_queues 程序执行"""
    while not QUIT:
        item = db.zrange('delayed:', 0, 0, withscores=True)
        if item[0][1] < time.time():
            time.sleep(.01)
            continue

        item = item[0][0]
        identifier, queue, name, args = json.loads(item)

        locked = acquire_lock(identifier)
        if not locked:
            continue

        if db.zrem('delayed:', item):
            db.rpush('queue:' + queue, item)

        release_lock(identifier, locked)
