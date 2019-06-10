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
