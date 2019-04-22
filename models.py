# -*- coding: utf-8 -*-
"""
Article:
    - `time:` 发布时间(排序， zset)
    - `score:` 评分(排序，zset)

Article_content:
    {
        "title": "",
        "link": "",
        "poster": "",
        "time": 1522211222,
        "votes": 1
    }
Group_article:
    - `group:programming`: 分类文章组（set）
    
"""
import time

from app import redis_db

ONE_WEEK_IN_SECONDS = 7 * 86400
VOTE_SCORE = 432

def article_vote(user, article):
    cutoff = time.time() - ONE_WEEK_IN_SECONDS
    if redis_db.zscore('time:', article) < cutoff:
        return
    
    article_id = article.partition(':')[-1]
    if redis_db.sadd('voted:' + article_id, user):
        redis_db.zincrby('score:', article, VOTE_SCORE)
        redis_db.hincrby(article, 'votes', 1)


def post_article(user, title, link):
    article_id = str(redis_db.incr('article:'))

    voted = 'voted:' + article_id
    redis_db.sadd(voted, user)
    redis_db.expire(voted, ONE_WEEK_IN_SECONDS)

    now = time.time()
    article = 'article:' + article_id
    redis_db.hmset(article, {
        'title': title,
        'link': link,
        'poster': user,
        'time': now,
        'votes': 1
    })

    redis_db.zadd('score:', article, now + VOTE_SCORE)
    redis_db.zadd('time:', article, now)

    return article_id


ARTICLE_PER_PAGE = 25

def get_articles(page, order='score:'):
    start = (page - 1) * ARTICLE_PER_PAGE
    end = start + ARTICLE_PER_PAGE + 1

    ids = redis_db.zrevrange(order, start, end)
    articles = []
    for id in ids:
        article_data = redis_db.hgetall(id)

        article_data['id'] = id
        articles.append(article_data)
    
    return articles


def add_remove_groups(article_id, to_add=None, to_remove=None):
    to_add = to_add or []
    to_remove = to_remove or []
    article = 'article:' + article_id
    for group in to_add:
        redis_db.sadd('group:' + group, article)
    for group in to_remove:
        redis_db.srem('group:' + group, article)


def get_group_articles(group, page, order='score:'):
    key = order + group
    if not redis_db.exists(key):
        redis_db.zinterstore(key, ['group:' + group, order], aggregate='max')
        redis_db.expire(key, 60)
    return get_articles(page, key)
