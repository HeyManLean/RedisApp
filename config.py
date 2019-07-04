# -*- coding: utf-8 -*-
"""
配置相关
"""

# ----------------- 系统配置 -----------------
# 1. 加密密钥
SECRET_KEY = 'heymanlean'
# 2. 开发相关
DEBUG = True
ENV = 'development'  # production, testing, development
TESTING = True


# ----------------- 用户相关 -----------------
# 1. Session
SESSION_EXPIRE_TIME = 3600 * 24


# ------------------ 数据库相关 -----------------
# 1. MongoDB
DEV_MONGO_URI = 'mongo://localhost:27017'
MONGO_DBS = {
    '1000': DEV_MONGO_URI,
}


# 2. Redis
DEV_REDIS_URI = 'redis://localhost:6379'
REDIS_DBS = {
    'ad': '%s/1' % DEV_REDIS_URI,
    'session': '%s/2' % DEV_REDIS_URI,
    'post': '%s/3' % DEV_REDIS_URI,
    'cache': '%s/4' % DEV_REDIS_URI,
    'conf': '%s/5' % DEV_REDIS_URI,
    'ip': '%s/6' % DEV_REDIS_URI,
    'counter': '%s/7' % DEV_REDIS_URI,
}

# 3. Mysql
MYSQL_DBS = {
    'default': {  # 默认 db
        'drivername': 'mysql+pymysql',
        'host': 'localhost',
        'port': '3306',
        'username': 'root',
        'password': '123456',
        'database': 'myapp',
        'query': {'charset': 'utf8mb4'}
    },
}


class Config(object):
    """供 flask 使用的配置"""
    SECRET_KEY = SECRET_KEY
    ENV = ENV
    TESTING = TESTING

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """初始化 flask 相关配置"""
        app.config.from_object(Config)
