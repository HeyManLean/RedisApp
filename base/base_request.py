# -*- coding: utf-8 -*-

from flask.wrappers import Request


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
