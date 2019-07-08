# -*- coding: utf-8 -*-
from datetime import datetime

from utils.words import tokenize
from utils.db import zunion, zintersect, union
from utils.ip import ip_to_score
from app import redis_mapping
from app.models.ad import Ad


redis_db = redis_mapping.get_db('ad')


def gen_ad_id():
    key = 'counter:ad_id'
    return str(redis_db.incr(key))


def get_ad(ad_id):
    ad = Ad.load(ad_id=ad_id)
    return ad


def add_ad(name, locations, content, type, value):
    ad_id = gen_ad_id()
    ad = Ad()
    ad.ad_id = ad_id
    ad.name = name
    ad.type = type
    ad.content = content
    ad.locations = locations
    ad.value = value

    ad.create_time = datetime.now()
    ad.update_time = datetime.now()

    data = ad.to_json()

    ad.save_new()

    # 建立广告搜索索引
    index_ad(ad_id, locations, content, type, value)

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
    pipeline.zadd('ad:ad_value:', {ad_id: rvalue})
    pipeline.execute()
    return True


def target_ads(locations, content):
    """广告定向"""
    pipeline = redis_db.pipeline()

    matched_ads, base_ecpm = match_location(pipeline, locations)
    words, target_ads = finish_scoring(
        pipeline, matched_ads, base_ecpm, content)

    pipeline.incr('ad:served:')  # 相当于生成一个订单
    pipeline.zrevrange(target_ads, 0, 0)

    target_id, targeted_ad = pipeline.execute()[-2:]
    target_id = str(target_id)

    if not targeted_ad:
        return None, None

    ad_id = targeted_ad[0]
    record_targeting_result(target_id, ad_id, words)

    return target_id, ad_id


def match_location(pipe, locations):
    location_items = ['idx:loc:' + location for location in locations]
    matched_ads = union(pipe, location_items, _execute=False)

    base_ecpm = zintersect(
        pipe, {matched_ads: 0, 'ad:ad_value:': 1}, _execute=False)
    return matched_ads, base_ecpm


def finish_scoring(pipe, matched, base, content):
    words = tokenize(content)
    bonus_ecpm = {}
    for word in words:
        word_key = 'idx:word:' + word
        word_bonu = zintersect(pipe, {word_key: 1, matched: 0}, _execute=False)
        bonus_ecpm[word_bonu] = 1

    if bonus_ecpm:
        maximum = zunion(pipe, bonus_ecpm, aggregate='MAX', _execute=False)
        minimum = zunion(pipe, bonus_ecpm, aggregate='MIN', _execute=False)

        target_ads = zunion(
            pipe, {maximum: 0.5, minimum: 0.5, base: 1}, _execute=False)
        return words, target_ads

    return words, base


def record_targeting_result(target_id, ad_id, words):
    """记录广告定向结果"""
    pipeline = redis_db.pipeline()
    terms = redis_db.smembers('ad:terms:' + ad_id)
    matched = list(terms & words)

    # 记录此次匹配的结果的命中单词
    if matched:
        matched_key = 'terms:matched:' + target_id
        pipeline.sadd(matched_key, *matched)
        pipeline.expire(matched_key, 900)

    # 更新类型查看次数
    type = redis_db.hget('ad:type:', ad_id)
    pipeline.incr('type:%s:views:' % type)

    # 更新广告每个单词查看次数, 以及总次数
    for word in matched:
        pipeline.zincrby('views:' + ad_id, 1, word)
    pipeline.zincrby('views:' + ad_id, 1, '')

    if not pipeline.execute()[-1] % 100:
        update_cpms(ad_id)


def record_click(target_id, ad_id, action=True):
    """记录广告点击"""
    pipeline = redis_db.pipeline()

    clicked_key = 'clicks:' + ad_id
    matched_key = 'terms:matched:' + target_id

    type = redis_db.hget('ad:type:', ad_id)
    if type == 'cpa':
        pipeline.expire(matched_key, 900)
        if action:
            clicked_key = 'actions:' + ad_id

    # 更新类型点击次数
    if action and type == 'cpa':
        pipeline.incr('type:%s:actions:' % type)
    else:
        pipeline.incr('type:%s:clicks:' % type)

    # 对于有效结果的单词, 更新点击次数及总次数
    matched = list(redis_db.smembers(matched_key))
    matched.append('')
    for word in matched:
        pipeline.zincrby(clicked_key, 1, word)

    pipeline.execute()

    update_cpms(ad_id)


def update_cpms(ad_id):
    """更新广告的ecpm"""
    pipeline = redis_db.pipeline()

    pipeline.hget('ad:type:', ad_id)
    pipeline.zscore('ad:base_value:', ad_id)
    pipeline.smembers('terms:' + ad_id)

    type, base_value, words = pipeline.execute()

    which = 'clicks'
    if type == 'cpa':
        which = 'actions'

    pipeline.get('type:%s:views' % type)
    pipeline.get('type:%s:%s' % (type, which))
    type_views, type_clicks = pipeline.execute()
    AVERAGE_PER_1K[type] = (
        1000. * int(type_clicks or '1') / int(type_views or '1'))

    if type == 'cpm':
        return

    view_key = 'views:' + ad_id
    click_key = '%s:%s' % (which, ad_id)

    to_ecpm = TO_ECPM[type]
    pipeline.zscore(view_key, '')
    pipeline.zscore(click_key, '')
    ad_views, ad_clicks = pipeline.execute()

    if (ad_clicks or 0) < 1:
        ad_ecpm = redis_db.zscore('ad:ad_value:', ad_id)
    else:
        ad_ecpm = to_ecpm(ad_views or 1, ad_clicks or 0, base_value)
        pipeline.zadd('ad:ad_value:', {ad_id: ad_ecpm})

    for word in words:
        pipeline.zscore(view_key, word)
        pipeline.zscore(click_key, word)
        views, clicks = pipeline.execute()

        if (clicks or 0) < 1:
            continue

        word_ecpm = to_ecpm(views or 1, clicks or 0, base_value)
        bonus = word_ecpm - ad_ecpm
        pipeline.zadd('idx:' + word, {ad_id: bonus})

    pipeline.execute()


MAX_SCORE = ip_to_score('255.255.255.255')


def ip_to_location(ip: str) -> str:
    """解析 ip 获取位置信息"""
    score = ip_to_score(ip)
    match = redis_db.zrangebyscore(
        'ip_location:', score, MAX_SCORE, 0, 1, withscores=True)

    if not match:
        return None
    else:
        return match[0][0].split('_')[0]
