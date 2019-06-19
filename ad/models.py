# -*- coding: utf-8 -*-
from app import mongo_db
from utils.db import DbModel, StringField, DatetimeField, IntegerField



class Ad(DbModel):
    """Ad数据模型"""
    __db__ = mongo_db
    __tablename__ = 'ad'

    ad_id = StringField(index=True)
    name = StringField()
    type = StringField()
    value = IntegerField()

    content = StringField()

    create_time = DatetimeField()
    update_time = DatetimeField()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.ad_id)
