# -*- coding: utf-8 -*-
"""
自定义错误
"""


class ParamError(Exception):
    def __init__(self, help=''):
        self.help = help or ''

        self.code = 10001
        self.errmsg = '参数检验失败!'

    def to_dict(self):
        res = {
            'code': self.code,
            'errmsg': self.errmsg,
        }
        if self.help:
            res['help'] = self.help
        return res


class UnAuthError(Exception):
    def __init__(self):
        self.code = 10002
        self.errmsg = '用户未登录！'

    def to_dict(self):
        res = {
            'code': self.code,
            'errmsg': self.errmsg,
        }
        return res
