#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
自动补全最近联系人
"""
from redis import Redis


db = Redis(decode_responses=True)


def add_update_contact(user, contact):
    ac_list = 'recent:' + user
    pipeline = db.pipeline(True)
    pipeline.lrem(ac_list, 0, contact)
    pipeline.lpush(ac_list, contact)
    pipeline.ltrim(ac_list, 0, 99)
    pipeline.execute()


def remove_contact(user, contact):
    db.lrem('recent:' + user, contact)


def fetch_autocomplete_list(user, prefix):
    candidates = db.lrange('recent:' + user, 0, -1)
    matches = []
    for candidate in candidates:
        if candidate.lower().startswith(prefix):
            matches.append(candidate)
    return matches


if __name__ == '__main__':
    add_update_contact('1', '156223428481')
    print(fetch_autocomplete_list('1', '15'))
