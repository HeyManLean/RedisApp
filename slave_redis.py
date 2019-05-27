#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid
import time

from redis import Redis


main_db = Redis(host='redis', port=6379)
slave_db1 = Redis(host='redis01', port=6379)
slave_db2 = Redis(host='redis02', port=6379)

# slave_db1.slaveof()  # 不指定host等, 则取消从库

slave_db1.slaveof(host='redis', port=6379)
slave_db2.slaveof(host='redis', port=6379)


def wait_for_sync(m_db, s_db):
    ident = str(uuid.uuid4())
    m_db.zadd('sync:wait', {ident: time.time()})

    while s_db.info()['master_link_status'] != 'up':
        time.sleep(.001)

    while not s_db.zscore('sync:wait', ident):
        time.sleep(.001)

    deadline = time.time() + 1.01
    while time.time() < deadline:
        if s_db.info().get('aof_pending_bio_fsync') == 0:
            break
        time.sleep(.001)

    m_db.zrem('sync:wait', ident)
    m_db.zremrangebyscore('sync:wait', 0, time.time() - 900)


if __name__ == '__main__':
    wait_for_sync(main_db, slave_db1)
    wait_for_sync(main_db, slave_db2)
