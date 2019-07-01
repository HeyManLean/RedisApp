# -*- coding: utf-8 -*-
"""
模块视图
"""

from .ad import ad_mod


def init_app(app):
    """初始化视图"""
    app.register_blueprint(ad_mod, url_prefix='/ads')
