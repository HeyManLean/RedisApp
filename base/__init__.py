# -*- coding: utf-8 -*-
"""
HTTP 基础工具
"""
import time
import logging
import json

from flask import g, request
from flask.wrappers import Request


class RequestClass(Request):
    def __init__(self, *args, **kwargs):
        self._params = {}
        self._token = None
        self._user_id = None

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

    def get_token(self):
        if self._token is None:
            self._token = self.cookies.get('token', '')

        return self._token

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value


class MyRequest(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.request_class = RequestClass


class HttpLog(object):
    def __init__(self, app=None):
        self.logger = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.logger = app.extensions.get('logger') or logging

        app.before_request(self.before_request)
        app.after_request(self.after_request)

        app.extensions['handler_middler'] = self

    def before_request(self):
        g.request_start_time = time.time()

    def after_request(self, response):
        if request.method == 'GET':
            req_data = request.args.to_dict()
        elif request.method == 'POST':
            req_data = request.json
        else:
            req_data = request.data

        req_data = json.dumps(req_data, ensure_ascii=False)

        resp_data = json.loads(response.get_data())
        resp_data = json.dumps(resp_data, ensure_ascii=False)

        waste_time = int((time.time() - g.request_start_time) * 1000)

        msg = '%s "%s %s %s %s %sms" - Req: %s, Resp: %s' % (
            request.ip, request.method, request.environ['SERVER_PROTOCOL'],
            request.full_path.strip('?'), response.status_code, waste_time,
            req_data, resp_data
        )

        self.logger.info(msg)

        return response
