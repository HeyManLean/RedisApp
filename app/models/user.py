# -*- coding: utf-8 -*-
"""
用户数据模型
"""
from utils.db import (
    DbModel, IntegerField, StringField, DatetimeField
)


class User(DbModel):
    """用户数据模型"""
    __dbname__ = 'myapp'
    __tablename__ = 'user'

    user_id = IntegerField(index=True)
    username = StringField()
    password = StringField()
    nickname = StringField()

    login_time = DatetimeField()
    create_time = DatetimeField()
    update_time = DatetimeField()

    def to_json(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'name': self.name,
            'posts': self.posts,
            'followers': self.followers,
            'followings': self.followings,
            'create_time': self.create_time
        }

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.user_id)
