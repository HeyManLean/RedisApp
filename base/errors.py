# -*- coding: utf-8 -*-
"""
自定义错误
"""
from base.response import RetDef, RetCode


class ParamError(Exception):
    def __new__(cls, help=''):
        return RetCode(10001, '参数不正确！', help=help)


class UnAuthError(Exception):
    def __new__(cls, *args, **kwargs):
        return RetDef.SIGNIN_REQUIRED
