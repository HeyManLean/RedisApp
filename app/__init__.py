# -*- coding: utf-8 -*-
import logging
# import os

from flask import Flask
from redis import Redis
import pymongo

from base import MyRequest
from base.errors import ErrorHandler
from config import Config
from .views import Views


redis_host = 'localhost'  # 'redis'
mongo_host = 'localhost'  # 'mongo
redis_db = Redis(host=redis_host, port=6379, decode_responses=True)
mongo_db = pymongo.MongoClient(host=mongo_host, port=27017)['my_app']


def create_app():
    app = Flask(__name__)
    app.request_class = MyRequest

    # 激活视图模块
    Views(app)

    # 加载配置
    Config(app)

    # 自定义错误响应处理
    ErrorHandler(app)

    @app.route('/')
    def index():
        key = 'show_me'
        redis_db.incr(key)
        value = redis_db.get(key)
        return 'I have been show for %s times!' % int(value)

    return app
