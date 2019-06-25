# -*- coding: utf-8 -*
import re


IP_PATTERN = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')


def ip_to_score(ip: str) -> int:
    """ip 地址解析成 int 数值"""
    if not ip:
        return 0

    matched = IP_PATTERN.match(ip)
    if not matched:
        return 0

    score = 0
    for piece in matched.groups():
        score = score * 256 + int(piece)

    return score
