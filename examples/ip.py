#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
ip 存储相关
"""
import csv
import json
from collections import defaultdict

from redis import Redis


db = Redis(decode_responses=True)


def ip_to_score(ip_address):
    score = 0
    for v in ip_address.split('.'):
        score = score * 256 + int(v, 10)
    return score


def import_ips_to_redis(filename):
    csv_file = csv.reader(open(filename, 'rb'))
    for count, row in enumerate(csv_file):
        start_ip = row[0] if row else ''
        if 'i' in start_ip.lower():
            continue
        if '.' in start_ip:
            start_ip = ip_to_score(start_ip)
        elif start_ip.isdigit():
            start_ip = int(start_ip, 10)
        else:
            continue

        city_id = row[2] + '_' + str(count)
        db.zadd('ip2cityid:', city_id, start_ip)


def import_cities_to_redis(filename):
    for row in csv.reader(open(filename, 'rb')):
        if len(row) < 4 or not row[0].isdigit():
            continue

        row = [i.decode('latin-1') for i in row]
        city_id = row[0]
        country = row[1]
        region = row[2]
        city = row[3]
        db.hset('cityid2city:', city_id, json.dumps([city, region, country]))


def find_city_by_ip(ip_address):
    if isinstance(ip_address, str):
        ip_address = ip_to_score(ip_address)

    city_id = db.zrevrangebyscore(
        'ip2cityid:', ip_address, 0, start=0, num=1
    )
    if not city_id:
        return None

    city_id = city_id[0].partition('_')[0]
    return json.loads(db.hget('cityid2city:', city_id))


def find_city_by_ip_local(ip):
    return find_city_by_ip(ip)


aggregates = defaultdict(lambda: defaultdict(int))


def daily_country_aggregate(line):
    if line:
        line = line.split()
        ip = line[0]
        day = line[1]
        country = find_city_by_ip_local(ip)
        aggregates[day][country] += 1
        return

    for day, aggregate in aggregates.items():
        db.zadd('daily:country:' + day, aggregate)
        del aggregates[day]
