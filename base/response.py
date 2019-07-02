# -*- coding: utf-8 -*-
"""
自定义响应
"""
# from collections import abc

from flask import jsonify


def render_response(obj, **kw):
    """渲染响应"""
    if isinstance(obj, RetCode):
        obj = obj.to_dict()
        obj.update(kw)

    return jsonify(obj)


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

    SIGNIN_REQUIRED = RetCode(10002, '用户未登录！')
    SIGNIN_FAILED = RetCode(10003, '用户名不存在或密码错误！')
    USER_EXISTS = RetCode(10010, '用户名已存在，请直接登录！')
