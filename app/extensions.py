# -*- coding: utf-8 -*-
"""
app 扩展工具
"""
import os
import logging.config

import pymongo
import redis
from flask_sqlalchemy import SQLAlchemy
from utils.db import DbModel

from config import (
    MONGO_DBS,
    REDIS_DBS,
    # MYSQL_DBS,
    LOG_PATH,
    LOGGING_CONF
)


class MongoMapping(object):
    """MongoDB 数据库获取工具

    Usage:
        >>> from app import mongo_mapping
        >>> mongo_db = mongo_mapping.get_db('myapp')
    """
    def __init__(self, app=None):
        self._conn_mapping = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        for conn_name, db_uri in MONGO_DBS.items():
            self._conn_mapping[conn_name] = pymongo.MongoClient(db_uri)

        DbModel.get_db = self.get_db
        app.extensions['mongo_mapping'] = self

    def get_db(self, db_name):
        return self._conn_mapping['1000'][db_name]


class RedisMapping(object):
    """Redis 数据库获取工具

    Usage:
        >>> from app import redis_mapping
        >>> redis_db = redis_mapping.get_db('session')
    """
    def __init__(self, app=None):
        self._conn_mapping = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        for db_name, db_uri in REDIS_DBS.items():
            self._conn_mapping[db_name] = redis.Redis.from_url(db_uri)
        app.extensions['mongo_mapping'] = self

    def get_db(self, db_name):
        return self._conn_mapping[db_name]


class MySQLAlchemy(SQLAlchemy):
    pass


class Logger(object):
    """日志工具

    Usage:
        >>> from app import logger
        >>> logger.info('User logined!')
        >>> logger.error('Something went wrong!')
    """
    def __init__(self, app=None):
        self.logger_mapping = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        # 关闭默认logger
        app_logger = logging.getLogger('werkzeug')
        app_logger.disabled = True

        if not os.path.isdir(LOG_PATH):
            os.makedirs(LOG_PATH)

        logging.config.dictConfig(LOGGING_CONF)
        self.logger_mapping = logging.root.manager.loggerDict

        app.extensions['logger'] = self

    def _log_common(self, levelname, msg, exc_info=False):
        if levelname in self.logger_mapping:
            logger = logging.getLogger(levelname)
        else:
            logger = logging.getLogger('default')
        getattr(logger, levelname)(msg, exc_info=exc_info)

    def info(self, msg, exc_info=False):
        self._log_common('info', msg, exc_info)

    def debug(self, msg, exc_info=False):
        self._log_common('debug', msg, exc_info)

    def warning(self, msg, exc_info=False):
        self._log_common('warning', msg, exc_info)

    def error(self, msg, exc_info=True):
        self._log_common('error', msg, exc_info)
