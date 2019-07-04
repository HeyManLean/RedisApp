# -*- coding: utf-8 -*-
"""
自定义错误
"""
from base.response import RetDef, RetCode, render_response


class ParamError(Exception):
    def __init__(self, help=''):
        self.retcode = RetCode(10001, '参数不正确！', help=help)


class UnAuthError(Exception):
    def __init__(self):
        self.retcode = RetDef.SIGNIN_REQUIRED


class ErrorHandler(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.register_error_handler(ParamError, self.handle_error)
        app.register_error_handler(UnAuthError, self.handle_error)

    def handle_error(error):
        """统一处理自定义错误响应码"""
        retcode = error.retcode
        return render_response(retcode)

    def handle_error500(error):
        """处理500错误"""
