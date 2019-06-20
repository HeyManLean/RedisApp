# -*- coding: utf-8 -*-
from datetime import datetime

from app import redis_db
from ad.models import Ad
from utils.words import tokenize


def gen_ad_id():
    key = 'counter:ad_id'
    return str(redis_db.incr(key))


def get_ad(ad_id):
    ad = Ad.load(ad_id=ad_id)
    return ad


def add_ad(name, desc, content, locations):
    ad_id = gen_ad_id()
    ad = Ad()
    ad.ad_id = ad_id
    ad.name = name
    ad.desc = desc
    ad.content = content

    ad.create_time = datetime.now()
    ad.update_time = datetime.now()

    data = ad.to_json()

    ad.save_new()

    # 建立广告搜索索引
    index_ad(ad_id, content, locations)

    return data


def update_ad(ad_id, **kwargs):
    ad = Ad.load(ad_id=ad_id)
    for key, value in kwargs:
        setattr(ad, key, value)
    ad.update_time = datetime.now()

    return True


def remove_ad(ad_id):
    Ad.remove(ad_id=ad_id)
    return True


def index_ad(ad_id, content, locations, type, value):
    """广告索引建立
    
    Args:
        ad_id (str): 广告id
        content (str): 广告内容
        locations (list): 地区列表, 如 guangzhou, shanghai, yangjiang
        type (str): 广告类型, cpm, cpc, cpa
        value (int): 广告价格
    """
    words = tokenize(content)

    


def target_ads():
    """广告定向"""


def record_targeting_result():
    """记录广告定向结果"""


def record_click():
    """记录广告点击"""


def update_ecpm():
    """更新广告的ecpm"""
