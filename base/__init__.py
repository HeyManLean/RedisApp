# -*- coding: utf-8 -*-
"""
HTTP 基础工具
"""
from functools import wraps
from collections import abc

from flask import request

from .errors import ParamError


class Argument(object):
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
        """解析并检查参数取值"""
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


def parse_args(*arguments):
    """解析请求参数
    Args:
        arguments: array of **Argument**
    """
    def middle(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            for argument in arguments:
                value = argument.load()
                request._params[argument.name] = value

            return func(*args, **kwargs)
        return decorated_func
    return middle
