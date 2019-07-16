# -*- coding: utf-8 -*-
"""
状态消息
"""
from enum import Enum
from utils.db import (
    DbModel, IntegerField, StringField, DatetimeField
)


class Status(DbModel):
    """状态消息数据模型"""
    __dbname__ = 'myapp'
    __tablename__ = 'status'

    status_id = IntegerField(index=True)
    user_id = IntegerField()
    nickname = StringField()
    content = StringField()

    publish_status = IntegerField()

    create_time = DatetimeField()
    update_time = DatetimeField()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.status_id)


class PublishStatus(Enum):
    INIT = 0
    PUBLISHED = 1
