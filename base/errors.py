# -*- coding: utf-8 -*-
"""
自定义错误
"""
from base.response import render_response


class ApiError(Exception):
    def __init__(self, code, help=None):
        self.code = code
        self.help = help


class ErrorHandler(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.register_error_handler(ApiError, self.handle_error)
        app.register_error_handler(500, self.handle_error500)

    @staticmethod
    def handle_error(error):
        """统一处理自定义错误响应码"""
        return render_response(
            error.code,
            help=error.help
        )

    @staticmethod
    def handle_error500(error):
        """处理500错误"""
        return error
