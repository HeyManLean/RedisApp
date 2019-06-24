# -*- coding: utf-8 -*-
from datetime import datetime

from app import redis_db
from ad.models import Ad
from utils.words import tokenize
from utils.db import zunion, zintersect, union, intersect


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


# ------------- 广告定向 ---------------
AVERAGE_PER_1K = {}


def cpc_to_cpm(views, clicks, cpc):
    return 1000. * (clicks / views) * cpc


def cpa_to_cpm(views, clicks, cpa):
    return 1000. * (clicks / views) * cpa


TO_ECPM = {
    'cpc': cpc_to_cpm,
    'cpa': cpa_to_cpm,
    'cpm': lambda *args: args[2]
}


def index_ad(ad_id, locations, content, type, value):
    """广告索引建立

    Args:
        ad_id (str): 广告id
        content (str): 广告内容
        locations (list): 地区列表, 如 guangzhou, shanghai, yangjiang
        type (str): 广告类型, cpm, cpc, cpa
        value (int): 广告价格
    """
    pipeline = redis_db.pipeline()
    words = tokenize(content)
    for word in words:
        pipeline.sadd('idx:word:' + word, ad_id)

    for location in locations:
        pipeline.sadd('idx:loc:' + location, ad_id)

    pipeline.sadd('ad:terms:' + ad_id, *words)
    pipeline.hset('ad:type:', ad_id, type)
    pipeline.zadd('ad:base_value:', {ad_id: value})

    rvalue = TO_ECPM[type](1000, AVERAGE_PER_1K.get(type, 1), value)
    pipeline.zadd('ad:ad_value:', ad_id, rvalue)
    pipeline.execute()
    return True


def target_ads(locations, content):
    """广告定向"""
    matched_ads, base_ecpm = match_location(locations)
    words, target_ads = finish_scoring(matched_ads, base_ecpm, content)

    ad_id = redis_db.zrevrange(target_ads, 0, 0)
    record_targeting_result(target_id, ad_id, words)
    return ad_id


def match_location(locations):
    location_items = ['idx:loc:' + location for location in locations]
    matched_ads = union(redis_db, location_items)
    return matched_ads, zintersect(
        redis_db, {matched_ads: 0, 'ad:ad_value:': 1})


def finish_scoring(matched, base, content):
    words = tokenize(content)
    bonus_ecpm = {}
    for word in words:
        word_bonu = zintersect(redis_db, {word: 1, matched: 0})
        bonus_ecpm[word_bonu] = 1

    if bonus_ecpm:
        maximum = zunion(redis_db, bonus_ecpm, aggregate='MAX')
        minimum = zunion(redis_db, bonus_ecpm, aggregate='MIN')

        return words, zunion(redis_db, {maximum: 0.5, minimum: 0.5, base: 1})

    return word, base


def record_targeting_result(target_id, ad_id, words):
    """记录广告定向结果"""


def record_click():
    """记录广告点击"""


def update_ecpm():
    """更新广告的ecpm"""
