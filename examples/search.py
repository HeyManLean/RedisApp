#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
搜索
"""
import re
import uuid

from redis import Redis


db = Redis(decode_responses=True)


STOP_WORDS = set('''able about across after all almost also am 
among an and any are as at be because been but by can cannot 
could dear did do does either else ever every for from get got 
had has have he her hers him his how howerver if in into is it its 
just least let like likely may me might most must my neither no 
nor not of off often on only or other our own rather said say says 
she should since so some than that the their them then there 
these they this tis to too twas us wants was we were what 
when where which while who whom why will with would yet you'''.split())


WORDS_RE = re.compile("[a-z']{2,}")


def tokenize(content):
    words = set()
    for match in WORDS_RE.finditer(content.lower()):
        word = match.group().strip("'")
        if len(word) >= 2:
            words.add(word)
    return words - STOP_WORDS


def index_document(docid, content):
    words = tokenize(content)

    pipeline = db.pipeline()
    for word in words:
        db.sadd('idx:' + word, docid)
    return len(pipeline.execute())


def _set_common(method, names, ttl=30, execute=True):
    id = str(uuid.uuid4())
    pipeline = db.pipeline if execute else db
    names = ['idx:' + name for name in names]
    getattr(pipeline, method)('idx:' + id, *names)
    pipeline.expire('idx:' + id, ttl)
    if execute:
        pipeline.execute()
    return id


def intersect(items, ttl=30, _execute=True):
    return _set_common('sinterstore', items, ttl, _execute)


def union(items, ttl=30, _execute=True):
    return _set_common('sunionstore', items, ttl, _execute)


def difference(items, ttl=30, _execute=True):
    return _set_common('sdiffstore', items, ttl, _execute)


QUERY_RE = re.compile("[+-]?[a-z']{2,}")


def parse(query):
    unwanted = set()
    all = []
    current = set()
    for match in QUERY_RE.finditer(query.lower()):
        word = match.group()
        prefix = word[:1]
        if prefix in '+-':
            word = word[1:]
        else:
            prefix = None

        word = word.strip("'")
        if len(word) < 2 or word in STOP_WORDS:
            continue
        if prefix == '-':
            unwanted.add(word)
            continue

        if current and not prefix:
            all.append(list(current))
            current = set()

        current.add(word)

    if current:
        all.append(list(current))

    return all, list(unwanted)


def parse_and_search(query, ttl=30):
    all, unwanted = parse(query)
    if not all:
        return None

    to_intersect = []
    for syn in all:
        if len(syn) > 1:
            to_intersect.append(union(syn), ttl=ttl)
        else:
            to_intersect.append(syn[0])

    if len(to_intersect) > 1:
        intersect_result = intersect(to_intersect, ttl=ttl)
    else:
        intersect_result = to_intersect[0]

    if unwanted:
        unwanted.insert(0, intersect_result)
        return difference(unwanted, ttl=ttl)

    return intersect_result


def search_and_sort(query, id=None, ttl=300, sort='-updated',
                    start=0, num=20):
    desc = sort.startswith('-')
    sort = sort.lstrip('-')
    by = 'kb:doc:*->' + sort  # * 指向集合的值, -> hash 字段排序
    alpha = sort not in ('updated', 'id', 'created')

    if id and not db.expire(id, ttl):
        id = None

    if not id:
        id = parse_and_search(query, ttol=ttl)

    pipeline = db.pipeline()
    pipeline.scard('idx:' + id)
    pipeline.sort(
        'idx:' + id, by=by, alpha=alpha,
        desc=desc, start=start, num=num)
    results = pipeline.execute()

    return results[0], results[1], id


def search_and_zsort(query, id=None, ttl=300, update=1, vote=0,
                     start=0, num=20, desc=True):
    if id and not db.expire(id, ttl):
        id = None

    if not id:
        id = parse_and_search(query, ttl=ttl)
        scored_search = {
            id: 0,
            'sort:update': update,
            'sort:votes': vote
        }
        id = zintersect(scored_search, ttl)

    pipeline = db.pipeline()
    pipeline.zcard('idx:' + id)
    if desc:
        pipeline.zrevrange('idx:' + id, start, start + num - 1)
    else:
        pipeline.zrange('idx:' + id, start, start + num - 1)
    results = pipeline.execute()

    return results[0], results[1], id


def _zset_common(method, scores, ttl=30, **kw):
    id = str(uuid.uuid4())
    execute = kw.pop('_execute', True)
    pipeline = db.pipeline() if execute else db
    for key in scores.keys():
        scores['idx:' + key] = scores.pop(key)

    getattr(pipeline, method)('idx:' + id, scores, **kw)
    pipeline.expire('idx:' + id, ttl)
    if execute:
        pipeline.execute()
    return id


def zintersect(items, ttl=30, **kw):
    return _zset_common('zinterstore', dict(items), ttl, **kw)


def zunion(items, ttl=30, **kw):
    return _zset_common('zunionstore', dict(items), ttl, **kw)


# ---- 广告搜索 ----
def cpc_to_ecpm(views, clicks, cpc):
    return 1000. * cpc * clicks / views


def cpa_to_ecpm(views, actions, cpa):
    return 1000. * cpa * actions / views


TO_ECPM = {
    'cpc': cpc_to_ecpm,
    'cpa': cpa_to_ecpm,
    'cpm': lambda *args: args[-1]
}


AVERAGE_PER_1K = {}


def index_ad(id, locations, content, type, value):
    """给广告建立索引
    Args:
        id: 广告id
        locations: 广告服务地区
        content: 广告文本内容
        type: 广告价格类型: cpa, cpc, cpm
        value: 广告价格(cpa的价格等)
    """
    pipeline = db.pipeline()

    for location in locations:
        pipeline.sadd('idx:req:' + location, id)

    words = tokenize(content)
    for word in words:
        pipeline.zadd('idx:' + word, id, 0)

    rvalue = TO_ECPM[type](
        1000, AVERAGE_PER_1K.get(type, 1), value)
    pipeline.hset('type:' + id, type)
    pipeline.zadd('idx:ad:value:', id, rvalue)  # eCPM(可附加)
    pipeline.zadd('ad:base_value:', id, value)  # 所有ad的基本价格(查询表)
    pipeline.sadd('terms:' + id, *list(words))  # 记录广告所有的单词, 可以用于移除或更新广告
    pipeline.execute()


def target_ads(locations, content):
    """广告定向"""
    pipeline = db.pipeline()
    matched_ads, base_ecpm = match_location(locations)
    words, target_ads = finish_scoring(matched_ads, base_ecpm, content)

    # 在pipeline相关操作执行之后才能获得结果的, 要用 pipeline 获取
    pipeline.incr('ads:served:')
    pipeline.zrevrange('idx:' + target_ads, 0, 0)
    target_id, targeted_ad = pipeline.execute()[-2:]
    if not targeted_ad:
        return None, None

    ad_id = targeted_ad[0]
    record_targeting_result(target_id, ad_id, words)

    return target_id, ad_id


def match_location(locations):
    """找出与位置匹配的广告及其eCPM"""
    required = ['idx:req:' + location for location in locations]
    matched_ads = union(required, ttl=300)
    return matched_ads, zintersect({matched_ads: 0, 'ad:value:': 1})


def finish_scoring(matched, base, content):
    """找到跟内容匹配的广告, 并加上附加值的 eCPM"""
    bonus_ecpm = []
    words = tokenize(content)
    for word in words:
        word_bonus = zintersect({word: 1, matched: 0})
        bonus_ecpm[word_bonus] = 1

    if bonus_ecpm:
        minimum = zunion(bonus_ecpm, aggregate='MIN')
        maximum = zunion(bonus_ecpm, aggregate='MAX')

        return words, zunion({
            base: 1, minimum: 1, maximum: 1
        })
    return words, base


def record_targeting_result(target_id, ad_id, words):
    """定向完成后的操作(定向成功后相当于用户查看了广告)"""
    pipeline = db.pipeline()

    terms = db.smembers('terms:' + ad_id)
    matched = list(words & terms)
    if matched:
        matched_key = 'terms:matched:%s' % target_id
        pipeline.sadd(matched_key, *matched)
        pipeline.expire(matched_key, 900)

    type = db.hget('type:', ad_id)
    pipeline.incr('type:%s:views:' % type)
    for word in matched:
        pipeline.zincrby('views:%s' % ad_id, word)
    pipeline.zincrby('views:%s' % ad_id, '')

    if not pipeline.execute()[-1] % 100:
        update_cpms(ad_id)


def record_click(target_id, ad_id, action=False):
    """上报点击广告动作"""
    pipeline = db.pipeline()
    click_key = 'clicks:%s' % ad_id

    match_key = 'terms:matched:%s' % target_id

    type = db.hget('type:', ad_id)
    if type == 'cpa':
        pipeline.expire(match_key, 900)
        if action:
            click_key = 'actions:%s' % ad_id

    if action and type == 'cpa':
        pipeline.incr('type:%s:actions:' % type)
    else:
        pipeline.incr('type:%s:clicks:' % type)

    matched = list(db.smembers(match_key))
    matched.append('')
    for word in matched:
        pipeline.zincrby(click_key, word)
    pipeline.execute()

    update_cpms(ad_id)


def update_cpms(ad_id):
    """更新广告 eCPM 和单词的 eCPM"""
    pipeline = db.pipeline()

    pipeline.hget('type:', ad_id)
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
        1000. * int(type_clicks or '1') / int(type_views or '1')
    )

    if type == 'cpm':
        return

    view_key = 'views:%s' % ad_id
    click_key = '%s:%s' % (which, ad_id)

    to_ecpm = TO_ECPM[type]

    pipeline.zscore(view_key, '')
    pipeline.zscore(click_key, '')
    ad_views, ad_clicks = pipeline.execute()
    if (ad_clicks or 0) < 1:
        ad_ecpm = db.zscore('idx:ad:value:', ad_id)
    else:
        ad_ecpm = to_ecpm(ad_views or 1, ad_clicks or 0, base_value)
        pipeline.zadd('idx:ad:value:', ad_id, ad_ecpm)

    for word in words:
        pipeline.zscore(view_key, word)
        pipeline.zscore(click_key, word)
        views, clicks = pipeline.execute()[-2:]

        if (clicks or 0) < 1:
            continue

        word_ecpm = to_ecpm(views or 1, clicks or 0, base_value)
        bonus = word_ecpm - ad_ecpm
        pipeline.zadd('idx:' + word, ad_id, bonus)

    pipeline.execute()


# ------ 职位搜索 ------
def index_job(job_id, skills):
    pipeline = db.pipeline()

    for skill in skills:
        pipeline.sadd('idx:skill:' + skill, job_id)

    pipeline.zadd('idx:jobs:req', job_id, len(set(skills)))
    pipeline.execute()

    return True


def find_jobs(candidate_skills):
    skills = {}
    for skill in candidate_skills:
        skills['skill:' + skill] = 1

    job_scores = zunion(skills)
    final_result = zintersect({job_scores: -1, 'job:req': 1})

    return db.zrangebyscore('idx:' + final_result, 0, 0)
