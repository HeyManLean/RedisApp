# -*- coding: utf-8 -*-
"""
单词处理工具
"""
import re


STOP_WORDS = set('''able about across after all almost also am 
among an and any are as at be because been but by can cannot 
could dear did do does either else ever every for from get got 
had has have he her hers him his how howerver if in into is it its 
just least let like likely may me might most must my neither no 
nor not of off often on only or other our own rather said say says 
she should since so some than that the their them then there 
these they this tis to too twas us wants was we were what 
when where which while who whom why will with would yet you'''.split())


WORDS_RE = re.compile("[a-z']{2,}")


def tokenize(content: str) -> list:
    """标记内容, 获取有意义的单词列表
    Args:
        content (str): 文本内容
    Returns:
        words (list): 单词列表
    """
    words = set()

    for match in WORDS_RE.finditer(content):
        word = match.group()
        if len(word) > 2:
            words.add(word)

    return words - STOP_WORDS
