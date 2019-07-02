# -*- coding: utf-8 -*-
"""
公用的一些视图处理相关方法
"""
from functools import wraps

from flask import request

from app.services.user import check_token
from base.response import render_response, RetDef


def logined(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        """需要登录的视图函数装饰器"""
        user_id = check_token(request.token)
        if not user_id:
            return render_response(RetDef.LOGIN_REQUIRED)

        request.user_id = user_id

        return func(*args, **kwargs)
    return decorator
