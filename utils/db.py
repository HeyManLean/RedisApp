# -*- coding: utf-8 -*-
"""
数据库相关工具
"""
import abc
import logging
from datetime import datetime

from utils.timetool import utc_time_to_local, local_time_to_utc, iosformat


logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    filemode='w',
    datefmt='%b %d-%Y %H:%M:%S',
    format='%(message)s'
)


class BaseField(object):
    def __init__(self, name=None, index=False, nullable=True):
        self._name = name
        self._nullable = nullable
        self._index = index

    def __get__(self, instance, ownner):
        if instance is None:
            return self
        else:
            return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value


class ValidatedField(abc.ABC, BaseField):
    def __set__(self, instance, value):
        value = self.validate(instance, value)
        super().__set__(instance, value)

    @abc.abstractmethod
    def validate(self, instance, value):
        """return validated value"""


class StringField(ValidatedField):
    def validate(self, instance, value):
        if not self._nullable and not value:
            raise ValueError('<%s: %s> can not be empty!' % (
                StringField.__name__, self._name))
        if value and not isinstance(value, str):
            raise ValueError('<%s: %s> must be a string!' % (
                StringField.__name__, self._name))
        return value


class IntegerField(ValidatedField):
    def validate(self, instance, value):
        if not isinstance(value, int):
            raise ValueError('<%s: %s> must be a integer!' % (
                StringField.__name__, self._name))
        return value


class DatetimeField(ValidatedField):
    def validate(self, instance, value):
        if not isinstance(value, datetime):
            raise ValueError('<%s: %s> must be a datetime object!' % (
                StringField.__name__, self._name))
        return value

    def __get__(self, instance, ownner):
        if instance is None:
            return self
        else:
            dt = instance.__dict__.get(self._name)
            if dt:
                dt = utc_time_to_local(dt)
            return dt

    def __set__(self, instance, value):
        value = self.validate(instance, value)
        instance.__dict__[self._name] = local_time_to_utc(value)


class DbModelMeta(type):
    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)
        if not all([cls.__db__, cls.__tablename__]):
            return

        cls.__table__ = cls.__db__[cls.__tablename__]
        for method_name in MONGO_METHODS:
            if hasattr(cls.__table__, method_name):
                method = getattr(cls.__table__, method_name)
                setattr(cls, method_name, method)

        for key, attr in attr_dict.items():
            if not isinstance(attr, BaseField):
                continue

            if not attr._name:
                attr._name = key
                cls.__fields__.add(key)
            if attr._index:
                cls.__index_keys__.add(key)


MONGO_METHODS = [
    'update_one', 'update_many', 'delete_one',
    'delete_many', 'distinct', 'aggregate'
]


class DbModel(metaclass=DbModelMeta):
    __db__ = None
    __tablename__ = None
    __fields__ = set()
    __index_keys__ = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        # 检查数据库和表名是否有效
        if not all([cls.__db__, cls.__tablename__]):
            assert NotImplemented

        return super().__new__(cls)

    def to_dict(self):
        data = {}
        for key in self.__fields__:
            data[key] = self.__dict__.get(key)
        return data

    def to_json(self):
        data = {}
        for key in self.__fields__:
            value = self.__dict__.get(key)
            if isinstance(value, datetime):
                value = iosformat(value)
            data[key] = value
        return data

    def save_new(self):
        data = self.to_dict()
        self.__table__.insert_one(data)

        return True

    @classmethod
    def remove(cls, **kwargs):
        query_dict = {}
        if cls.__index_keys__ & set(kwargs) != cls.__index_keys__:
            return False

        query_dict = {}
        for key in cls.__index_keys__:
            query_dict[key] = kwargs[key]

        if query_dict:
            cls.delete_one(query_dict)
        return True

    @classmethod
    def load(cls, **kwargs):
        instance = cls()

        if cls.__index_keys__ & set(kwargs) != cls.__index_keys__:
            return instance

        query_dict = {}
        for key in cls.__index_keys__:
            query_dict[key] = kwargs[key]

        doc = cls.query_one(query_dict)
        if not doc:
            return instance

        for field in cls.__fields__:
            instance.__dict__[field] = doc.get(field)

        return instance

    @classmethod
    def _parse_sort_list(cls, sort_list):
        if sort_list:
            sorts = []
            for item in sort_list:
                desc = item.startswith('-')
                field = item.lstrip('-')

                if desc:
                    sign = -1
                else:
                    sign = 1
                sorts.append((field, sign))
            return sorts
        return None

    @classmethod
    def query_by_page(cls, filter_dict, sort_list=None, page=0, page_size=20):
        base_query = cls.__table__.find(filter_dict)
        total = base_query.count()

        sort_list = cls._parse_sort_list(sort_list)
        if sort_list:
            base_query = base_query.sort(sort_list)
        if page:
            offset = (page - 1) * page_size
            base_query = base_query.skip(offset).limit(page_size)

        return {
            'page': page,
            'page_size': page_size,
            'total': total,
            'items': [item for item in base_query]
        }

    @classmethod
    def query(cls, filter_dict, sort_list=None, execute=True):
        base_query = cls.__table__.find(filter_dict)

        sort_list = cls._parse_sort_list(sort_list)
        if sort_list:
            base_query = base_query.sort(sort_list)

        if execute:
            return [item for item in base_query]
        else:
            return base_query

    @classmethod
    def query_one(cls, filter_dict, sort_list=None):
        sort_list = cls._parse_sort_list(sort_list)
        if sort_list:
            return cls.__table__.find_one(filter_dict, sort=sort_list)

        return cls.__table__.find_one(filter_dict)
