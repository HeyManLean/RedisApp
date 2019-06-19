# -*- coding: utf-8 -*-
"""
基础 redis 操作
"""
from redis import Redis

conn = Redis(decode_responses=True)

def try_string():
    """字符串
    >>> from redis import Redis
    >>> conn = Redis()
    >>> conn.get('key')
    >>> conn.incr('key')
    1
    >>> conn.incrby('key', 15)
    16
    >>> conn.get('key')
    b'16'
    >>> conn.decr('key')
    15
    >>> conn.decrby('key', 4)
    11
    >>> type(conn.decrby('key', 4))
    <class 'int'>
    >>> conn.get('key')
    b'7'
    >>> conn.set('key', '13')
    True
    >>> conn.incr('key')
    14
    >>> conn.append('key', '->value')
    9
    >>> conn.get('key')
    '14->value'
    >>> conn.setrange('key', 0, 'H')
    9.
    >>> conn.get('key') 0 
    'H4->value'
    >>> conn.getrange('key', 5, 10)
    'alue'
    >>> conn.setbit('another-key', 2, 1)
    0
    >>> conn.setbit('another-key', 7, 1)
    0
    >>> conn.get('another-key')
    '!'
    """


def try_list():
    """列表

    """