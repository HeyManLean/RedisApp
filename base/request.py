# -*- coding: utf-8 -*-
from functools import wraps

from flask.wrappers import Request


class RequestParam(object):
    """请求参数对象"""
    __slots__ = [
        'name', 'type', 'required', 'default',
        'ignore', 'choices', 'by', 'help'
    ]

    def __init__(
        self,
        request,
        name,
        type=str,
        required=False,
        default=None,
        ignore=False,
        choices=None,
        by=None,
        help=None
    ):
        self.request = request
        self.name = name
        self.type = type
        self.required = required
        self.default = default
        self.ignore = ignore
        self.choices = choices
        self.by = by
        self.help = help

    def parse(self):
        self._params


class MyRequest(Request):
    def __init__(self, *args, **kwargs):
        self.__fields = []
        super().__init__(*args, **kwargs)
        self._ip = None

    @property
    def ip(self):
        if not self._ip:
            _ip = self.environ.get('HTTP_X_FORWARDED_FOR')
            if not _ip:
                _ip = self.environ.get('HTTP_X_REAL_IP', self.remote_addr)
            if ',' in _ip:
                _ip = _ip.split(',')[0]

            self._ip = _ip
        return self._ip

    @property
    def user_agent(self):
        return self.headers.get('User-Agent')

    @property
    def host(self):
        return self.headers.get('Host')

    def add_param(
        self,
        name,
        *,
        type=str,
        required=False,
        default=None,
        ignore=False,
        choices=None,
        by=None,
        help=None
    ):
        """
        Args:
            name (str): 字段名
            type (class): 类型
            required (bool): 是否必填
            default (any): 默认值 (必填时无效)
            ignore (bool): 是否忽略类型
            choices (tuple): 可选值
            by (str): 访问数据源 args, json, form
                      默认 GET: args, POST: json
            help (str): 参数不匹配时, 返回提示
        """
        self.__fields.append(
            RequestParam(
                request=self,
                name=name,
                type=type,
                required=required,
                default=default,
                ignore=ignore,
                choices=choices,
                by=by,
                help=help
            )
        )

        def middle(func):
            @wraps
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return middle

    _params = None

    @property
    def params(self):
        """获取参数"""
        if self._params is None:
            self._params = {}
            for field in self.__fields:
                pass

        return self._params
