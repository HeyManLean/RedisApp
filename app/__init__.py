# -*- coding: utf-8 -*-
from flask import Flask

from base import MyRequest, HttpLog
from base.errors import ErrorHandler
from config import Config
from app.views import MyApi
from app.extensions import (
    MongoMapping,
    RedisMapping,
    MySQLAlchemy,
    Logger
)

# 供其他模块调用的工具
mongo_mapping = MongoMapping()
redis_mapping = RedisMapping()
db = MySQLAlchemy()
logger = Logger()


def create_app():
    app = Flask(__name__)

    mongo_mapping.init_app(app)
    redis_mapping.init_app(app)
    db.init_app(app)
    logger.init_app(app)

    # 加载配置
    Config(app)

    # 请求模块
    MyRequest(app)
    # 激活视图模块
    MyApi(app)
    # 自定义错误响应处理
    ErrorHandler(app)
    # 请求处理日志
    HttpLog(app)

    @app.route('/')
    def index():
        redis_db = redis_mapping.get_db('test')
        key = 'show_me'
        redis_db.incr(key)
        value = redis_db.get(key)
        return 'I have been show for %s times!' % int(value)

    return app
