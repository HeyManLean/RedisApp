# -*- coding: utf-8 -*-
"""
时间相关处理工具
"""
import pytz
from datetime import datetime


DATETIME_PATTERN = '%Y-%m-%d %H:%M:%S'


def iosformat(dt: datetime):
    return dt.strftime(DATETIME_PATTERN)


def utc_time_to_local(dt: datetime, local_timezone="Asia/Shanghai"):
    """把utc datetime 转换为本地市区的时间"""
    return dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(local_timezone))


def local_time_to_utc(dt: datetime, local_timezone="Asia/Shanghai"):
    tz = pytz.timezone(local_timezone)
    return tz.localize(dt)
