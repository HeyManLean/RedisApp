# -*- coding: utf-8 -*-
"""
模块视图
"""


class Views(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """初始化视图"""
        from .ad import ad_mod
        from .user import user_mod

        app.register_blueprint(user_mod, url_prefix='/users')
        app.register_blueprint(ad_mod, url_prefix='/ads')
