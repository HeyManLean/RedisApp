# -*- coding: utf-8 -*-
"""
HTTP 基础工具
"""
from functools import wraps
from collections import abc

from flask import request
from flask.wrappers import Request

from .errors import ParamError


class Param(object):
    __slots__ = [
        'name', 'type', 'required', 'default', 'discard',
        'ignore', 'choices', 'by', 'help', 'nullable'
    ]

    def __init__(
        self,
        name,
        type=str,
        required=False,
        default=None,
        nullable=True,
        ignore=False,
        choices=None,
        by=None,
        discard=False,
        help=''
    ):
        """请求参数对象

        Args:
            name (str): 字段名
            type (class): 类型
            required (bool): 是否必填
            default (any): 默认值 (必填时无效)
            nullable (bool): 是否非空
            ignore (bool): 是否忽略类型
            choices (tuple): 可选值
            by (str): 访问数据源 args, json, form
                      默认 GET: args, POST: json
            discard (bool): 不存在 key, 是否不解析参数
            help (str): 参数不匹配时, 返回提示
        """
        self.name = name
        self.type = type
        self.required = required
        self.default = default
        self.ignore = ignore
        self.choices = choices
        self.nullable = nullable
        self.by = by
        self.discard = discard
        self.help = help

    def load(self):
        """解析并检查参数取值
        Returns:
            value(值), valid(是否有效)
        """
        if self.by and hasattr(request, self.by):
            req_data = getattr(request, self.by)
        elif request.method == 'GET':
            req_data = request.args
        else:
            req_data = request.json

        value = self.default

        # 检查是否存在此参数
        if req_data and self.name in req_data:
            value = req_data[self.name]
        elif self.required:
            raise ParamError(
                '`%s` is required! %s' % (self.name, self.help)
            )
        elif self.discard:
            return None, False

        # 检查是否非空
        if value is None:
            if not self.nullable:
                raise ParamError(
                    '`%s` is not nullable! %s' % (self.name, self.help)
                )

        # 检查参数类型
        elif not self.ignore and not isinstance(value, self.type):
            raise ParamError(
                'TypeError: `%s` is %s! %s' % (self.name, self.type, self.help)
            )

        # 检查取值
        if isinstance(self.choices, abc.Iterable) and\
                value not in self.choices:
            raise ParamError(
                'ValueError: `%s` must in %s!%s' % (
                    self.name, self.choices, self.help)
            )

        return value, True


def parse_params(*params):
    """解析请求参数
    Args:
        params: array of **Param**
    """
    def middle(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            for param in params:
                value, valid = param.load()
                if valid:
                    request._params[param.name] = value
            return func(*args, **kwargs)
        return decorated_func
    return middle


class MyRequest(Request):
    def __init__(self, *args, **kwargs):
        self._params = {}

        super().__init__(*args, **kwargs)

    @property
    def ip(self):
        _ip = self.environ.get('HTTP_X_FORWARDED_FOR')
        if not _ip:
            _ip = self.environ.get('HTTP_X_REAL_IP', self.remote_addr)
        if ',' in _ip:
            _ip = _ip.split(',')[0]

        return _ip

    @property
    def user_agent(self):
        return self.headers.get('User-Agent')

    @property
    def host(self):
        return self.headers.get('Host')

    @property
    def params(self):
        """获取参数"""
        return self._params
