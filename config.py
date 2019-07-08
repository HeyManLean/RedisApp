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


# ----------------- 辅助工具 -----------------
# 1. 日志
LOGGING_CONF = {
}


# ------------------ 数据库相关 -----------------
# 1. MongoDB
MONGO_DBS = {
    '1000': 'mongodb://localhost:27017',
}


# 2. Redis
REDIS_DBS = {
    'ad': 'redis://localhost:6379/1',
    'session': 'redis://localhost:6379/2',
    'post': 'redis://localhost:6379/3',
    'cache': 'redis://localhost:6379/4',
    'conf': 'redis://localhost:6379/5',
    'ip': 'redis://localhost:6379/6',
    'counter': 'redis://localhost:6379/7',
    'test': 'redis://localhost:6379/10',
}

# 3. Mysql
MYSQL_DBS = {
    'default': 'mysql+pymsql://root:123456@127.0.0.1:3306/myapp',
}


# --------------- Flask 相关配置 --------------
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
