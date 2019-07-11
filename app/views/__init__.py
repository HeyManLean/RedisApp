# -*- coding: utf-8 -*-
"""
模块视图
"""
from flask_restful import Api


class MyApi(Api):
    def init_app(self, app):
        """初始化视图"""
        super().init_app(app)

        from .user import UserResource, SessionResource
        from .ad import AdResource, SingleAdResource

        # 用户相关
        self.add_resource(UserResource, '/users')
        self.add_resource(SessionResource, '/session')

        # 广告相关
        self.add_resource(AdResource, '/ads')
        self.add_resource(SingleAdResource, '/ads/<string:ad_id>')
