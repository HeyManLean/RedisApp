# -*- coding: utf-8 -*-
"""
自定义响应
"""
# from collections import abc
from flask import jsonify

import config


def render_response(obj, data=None, help=None, cookies=None):
    """渲染响应

    Args:
        data (any): 返回数据
        help (str): 错误帮助提示
        cookies (dict): 要设置的 cookie 键值对
    """
    if not isinstance(obj, RetCode):
        assert 'render_response only accept `RetCode`.'

    ret_data = obj.to_dict()

    if data is not None:
        ret_data['data'] = data

    if help:
        ret_data['help'] = help

    response = jsonify(ret_data)
    if cookies:
        for key, value in cookies.items():
            response.set_cookie(
                key, value,
                max_age=config.SESSION_EXPIRE_TIME
            )

    return response


class RetCode(object):
    """响应码对象"""
    def __init__(self, code=0, msg='success', **extra):
        self.code = code
        self.msg = msg
        self.extra = extra

    def to_dict(self):
        res = {
            'code': self.code,
            'msg': self.msg,
            **self.extra
        }

        return res


class RetDef(object):
    SUCCESS = RetCode()

    PARAM_ERROR = RetCode(10001, '参数不正确！')

    LOGIN_REQUIRED = RetCode(10002, '用户未登录！')
    USER_EXISTS = RetCode(10010, '用户名已存在，请直接登录！')
    USER_NOT_FOUND = RetCode(10011, '用户名不存在或密码错误！')
