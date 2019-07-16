# -*- coding: utf-8 -*-
"""
配置相关
"""
import os

# ----------------- 系统配置 -----------------
# 1. 加密密钥
SECRET_KEY = 'heymanlean'
# 2. 开发相关
DEBUG = True
ENV = 'development'  # production, testing, development
TESTING = True

# 3. 项目路径
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
# 4. 日志路径（默认项目路径下 log 文件夹)
LOG_PATH = os.path.join(PROJECT_PATH, 'log')


# ----------------- 用户相关 -----------------
# 1. Session
SESSION_EXPIRE_TIME = 3600 * 24


# ----------------- 辅助工具 -----------------
# 1. 日志
LOGGING_CONF = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '[%(levelname)s] %(asctime)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'default_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': os.path.join(LOG_PATH, 'default.log')
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': os.path.join(LOG_PATH, 'error.log')
        }
    },
    'loggers': {
        # 按需求添加 warning 相关
        'default': {
            'level': 'DEBUG',
            'handlers': ['stdout', 'default_file'],
            'propagate': False
        },
        'error': {
            'level': 'ERROR',
            'handlers': ['stdout', 'error_file'],
            'propagate': False
        }
    }
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
    'status': 'redis://localhost:6379/3',
    'cache': 'redis://localhost:6379/4',
    'conf': 'redis://localhost:6379/5',
    'ip': 'redis://localhost:6379/6',
    'counter': 'redis://localhost:6379/7',
    'lock': 'redis://localhost:6379/8',
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
