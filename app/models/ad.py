# -*- coding: utf-8 -*-
from utils.db import (
    DbModel, StringField, DatetimeField,
    BaseField, FloatField
)


class Ad(DbModel):
    """Ad数据模型"""
    __dbname__ = 'myapp'
    __tablename__ = 'ad'

    ad_id = StringField(index=True)
    name = StringField()
    type = StringField()
    value = FloatField()

    content = StringField()
    locations = BaseField()

    create_time = DatetimeField()
    update_time = DatetimeField()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.ad_id)
