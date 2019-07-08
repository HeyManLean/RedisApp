# -*- coding: utf-8 -*-
"""
用户数据模型
"""
from app import mongo_mapping
from utils.db import (
    DbModel, IntegerField, StringField, DatetimeField
)


mongo_db = mongo_mapping.get_db('myapp')


class User(DbModel):
    """用户数据模型"""
    # TODO 这里可以改成数据库名，额外获取 db
    __db__ = mongo_db
    __tablename__ = 'user'

    user_id = IntegerField(index=True)
    username = StringField()
    password = StringField()

    login_time = DatetimeField()
    create_time = DatetimeField()
    update_time = DatetimeField()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.user_id)
