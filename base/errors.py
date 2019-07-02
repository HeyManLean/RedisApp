# -*- coding: utf-8 -*-
"""
自定义错误
"""
from base.response import RetDef, RetCode


class ParamError(Exception):
    def __init__(self, help=''):
        self.retcode = RetCode(10001, '参数不正确！', help=help)


class UnAuthError(Exception):
    def __init__(self):
        self.retcode = RetDef.SIGNIN_REQUIRED
