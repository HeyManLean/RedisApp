# -*- coding: utf-8 -*-
"""
字符串处理
"""
import random
import hashlib


CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def get_random_str(length=12, chars=''):
    """获取随机字符串"""
    chars = chars or CHARACTERS
    return ''.join([random.choice(chars) for _ in range(length)])


def get_hash_str(string, salt=''):
    """获取字符串 hash 值"""
    string += salt
    return hashlib.sha256(string.encode()).hexdigest()
