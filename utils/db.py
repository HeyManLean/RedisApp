# -*- coding: utf-8 -*-
"""
数据库相关工具
"""
import time
import math
import abc
from datetime import datetime, timedelta
import uuid
import binasciiG

from redis.exceptions import WatchError

from utils.timetool import utc_time_to_local, local_time_to_utc, iosformat


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
            raise ValueError('<%s: %s> must be a string! Not %s(%s)!' % (
                StringField.__name__, self._name, type(value), value))
        return value


class IntegerField(ValidatedField):
    def validate(self, instance, value):
        if not isinstance(value, int):
            raise ValueError('<%s: %s> must be a integer! Not %s(%s)!' % (
                StringField.__name__, self._name, type(value), value))
        return value


class FloatField(ValidatedField):
    def validate(self, instance, value):
        if not isinstance(value, float):
            raise ValueError('<%s: %s> must be a float! Not %s(%s)!' % (
                StringField.__name__, self._name, type(value), value))
        return value


class DatetimeField(ValidatedField):
    def validate(self, instance, value):
        if value and not isinstance(value, datetime):
            raise ValueError('<%s: %s> must be a datetime object! Not %s(%s)!' % (
                StringField.__name__, self._name, type(value), value))
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
        if value:
            instance.__dict__[self._name] = local_time_to_utc(value)
        else:
            instance.__dict__[self._name] = value


class DbModelMeta(type):

    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)
        if not all([cls.__dbname__, cls.__tablename__]):
            return

        cls.__db__ = cls.get_db(cls.__dbname__)

        cls.__table__ = cls.__db__[cls.__tablename__]
        for method_name in MONGO_METHODS:
            if hasattr(cls.__table__, method_name):
                method = getattr(cls.__table__, method_name)
                setattr(cls, method_name, method)

        cls.__index_keys__ = set()
        cls.__fields__ = set()
        for key, attr in attr_dict.items():
            if not isinstance(attr, BaseField):
                continue

            if not attr._name:
                attr._name = key
                cls.__fields__.add(key)
            if attr._index:
                cls.__index_keys__.add(key)


MONGO_METHODS = [
    'insert_one', 'update_one', 'update_many', 'delete_one',
    'delete_many', 'distinct', 'aggregate'
]


class DbModel(metaclass=DbModelMeta):
    __dbname__ = None
    __tablename__ = None

    # 不需要处理
    __fields__ = None
    __index_keys__ = None
    __db__ = None

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
            data[key] = getattr(self, key)
        return data

    def to_json(self):
        data = {}
        for key in self.__fields__:
            value = getattr(self, key)
            if isinstance(value, datetime):
                value = iosformat(value)
            data[key] = value
        return data

    def save_new(self):
        data = self.to_dict()
        self.insert_one(data)

        return True

    def update(self):
        query_dict = self._get_query_dict()
        update_dict = self.to_dict()
        self.update_one(query_dict, {'$set': update_dict})

        return update_dict

    def _get_query_dict(self):
        query_dict = {}
        for key in self.__index_keys__:
            query_dict[key] = getattr(self, key)

        return query_dict

    @classmethod
    def remove(cls, **kwargs):
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
        doc = cls.query_one(kwargs)
        if not doc:
            return None

        instance = cls()
        for field in cls.__fields__:
            setattr(instance, field, doc.get(field))

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


def _zset_common(conn, method, scores, ttl=30, **kw):
    id = 'idx:' + str(uuid.uuid4())
    execute = kw.pop('_execute', True)  # 是否有 excute
    # pipeline = conn.pipeline() if execute else conn
    pipeline = conn
    getattr(pipeline, method)(id, scores, **kw)
    pipeline.expire(id, ttl)
    if execute:
        pipeline.execute()
    return id


def zintersect(conn, items, ttl=30, **kw):
    return _zset_common(conn, 'zinterstore', dict(items), ttl, **kw)


def zunion(conn, items, ttl=30, **kw):
    return _zset_common(conn, 'zunionstore', dict(items), ttl, **kw)


def _set_common(conn, method, items, ttl=30, **kw):
    id = 'idx:' + str(uuid.uuid4())
    execute = kw.pop('_execute', True)  # 是否有 excute
    # pipeline = conn.pipeline() if execute else conn
    pipeline = conn
    getattr(pipeline, method)(id, items, **kw)
    pipeline.expire(id, ttl)
    if execute:
        pipeline.execute()
    return id


def intersect(conn, items, ttl=30, **kw):
    return _zset_common(conn, 'sinterstore', items, ttl, **kw)


def union(conn, items, ttl=30, **kw):
    return _set_common(conn, 'sunionstore', items, ttl, **kw)


def acquire_lock(db, lockname, acquire_timeout=10):
    """请求加锁

    Args:
        - db: db 连接
        - lockname: 需要加锁的键名
        - acquire_timeout: 加锁动作超时时间(类似 requests 的 timeout)
    Returns:
        - identifier (str): 动作标识
    """
    identifier = str(uuid.uuid4())
    lockname = 'lock:' + lockname

    end = time.time() + acquire_timeout
    while time.time() < end:
        if db.setnx(lockname, identifier):
            return identifier

        time.sleep(.001)
    return False


def acquire_lock_with_timeout(
        db, lockname, acquire_timeout=10, lock_timeout=10):
    """请求加锁, 并设置过期时间

    Args:
        - db: db 连接
        - lockname: 需要加锁的键名
        - acquire_timeout: 加锁动作超时时间(类似 requests 的 timeout)
        - lock_timeout: 成功加锁后, 对锁键设置过期时间
    Returns:
        - identifier (str): 动作标识
    """
    identifier = str(uuid.uuid4())
    lock_timeout = int(math.ceil(lock_timeout))
    lockname = 'lock:' + lockname

    end = time.time() + acquire_timeout
    while time.time() < end:
        if db.setnx(lockname, identifier):
            db.expire(lockname, lock_timeout)
            return identifier
        elif db.ttl(lockname) <= 0:
            db.expire(lockname, lock_timeout)

        time.sleep(.001)
    return False


def release_lock(db, lockname, identifier, timeout=10):
    """释放锁"""
    pipe = db.pipeline()
    lockname = 'lock:' + lockname

    end = time.time() + timeout
    while time.time() < end:
        try:
            pipe.watch(lockname)
            if pipe.get(lockname) == identifier:
                pipe.multi()
                pipe.delete(lockname)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except WatchError:
            pass
    return False


def shard_key(base, key, total_elements: int, shard_size: int):
    """分片key
    base: 存储的键名
    key: 要分片的索引id, 如 uid
    total_elements: 元素总数（最大值)
    shard_size: 每个分片大小
    """
    if isinstance(key, int) or key.isdigit():
        shard_id = int(key, 10) // shard_size
    else:
        shard = total_elements // shard_size
        # 计算唯一值（假设)
        shard_id = binascii.crc32(key.encode()) % shard
    return '%s:%s' % (base, shard_id)


def shard_hget(db, base, key, total_elements, shard_size):
    shard = shard_key(base, key, total_elements, shard_size)
    return db.hget(shard, key)


def shard_hset(db, base, key, value, total_elements, shard_size):
    shard = shard_key(base, key, total_elements, shard_size)
    return db.hset(shard, key, value)


def shard_sadd(db, base, member, total_elements, shard_size):
    shard = shard_key(base, 'x' + str(member), total_elements, shard_size)
    return db.sadd(shard, member)


SHARD_SIZE = 512


def count_size(db, session_id):
    today = datetime.today()
    key = 'unique:%s' % today.isoformat()
    expected = get_expected_size(db, key, today)
    member = int(session_id.replace('-', '')[:15], 16)
    if shard_sadd(db, key, member, expected, SHARD_SIZE):
        db.incr(key, 1)


EXPECTED_SIZES = {}
DEFAULT_SIZE = 100000


def get_expected_size(db, key, date):
    ex_key = key + ':expect'
    if ex_key in EXPECTED_SIZES:
        return EXPECTED_SIZES[ex_key]

    expected = db.get(ex_key)
    if not expected:
        yesterday = (date - timedelta(days=1)).isoformat()
        expected = db.get('unique:%s' % yesterday)
        expected = int(expected or DEFAULT_SIZE)

        expected = 2 ** math.ceil(math.log(expected * 1.5, 2))
        if not db.setnx(ex_key, expected):
            expected = db.get(ex_key)
        EXPECTED_SIZES[ex_key] = expected
    return expected
    