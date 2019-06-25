# -*- coding: utf-8 -*-
"""
文件相关工具
"""
import os


def count_lines(filename: str) -> int:
    """计算文件行数"""
    cnt = 0
    if os.path.isfile(filename):
        cnt = int(os.popen(
            'grep -c ^ %s' % filename).read().strip())
    return cnt
