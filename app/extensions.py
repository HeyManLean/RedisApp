# -*- coding: utf-8 -*-
"""
app 扩展工具
"""
import logging

import pymongo
import redis
from flask_sqlalchemy import SQLAlchemy

from config import (
    MONGO_DBS,
    REDIS_DBS,
    MONGO_DBS,
    LOGGING_CONF
)


class MongoMapping(object):
    def __init__(self, app=None):
        self._conn_mapping = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        for conn_name, db_uri in MONGO_DBS.items():
            self._conn_mapping[conn_name] = pymongo.MongoClient(db_uri)
        app.extensions['mongo_mapping'] = self

    def get_db(self, db_name):
        return self._conn_mapping['1000'][db_name]


class RedisMapping(object):
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
    """日志工具"""
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['logger'] = self
