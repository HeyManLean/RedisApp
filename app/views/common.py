# -*- coding: utf-8 -*-
"""
公用的一些视图处理相关方法
"""
from functools import wraps

from flask import request

from app.services.user import check_token
from base.errors import UnAuthError


def logined(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        """需要登录的视图函数装饰器"""
        token = request.get_token()
        user_id = check_token(token)
        if not user_id:
            raise UnAuthError

        request.user_id = user_id

        return func(*args, **kwargs)
    return decorator
