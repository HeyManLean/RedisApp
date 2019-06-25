#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
解析 ip 文件, 存储到 redis
"""
import sys
sys.path.append('..')


from utils.file import count_lines
from app import app, redis_db


IP_TEXT = '../temp/ip.txt'


def load_ip_to_redis(filename=IP_TEXT, flush=True):
    """解析ip, 存储到 redis"""
    lines = count_lines(filename)

    if flush:
        redis_db.delete('ip_location:')
        redis_db.delete('location:')

    with open(filename, 'r') as fp:
        ip_mapping = {}
        location_mapping = {}
        temp_location = None
        for count, line in enumerate(fp):
            if not line:
                continue

            pieces = line.split(',')
            score = pieces[1]
            country, province, city = pieces[4:7]

            location = city or province or country

            if location == temp_location:
                continue
            else:
                temp_location = location

            ip_mapping['%s_%s' % (location, count)] = score
            location_mapping[location] = '%s:%s:%s' % (country, province, city)

            if not count % 10000:
                redis_db.zadd('ip_location:', ip_mapping)
                redis_db.hmset('location:', location_mapping)

                ip_mapping = {}
                location_mapping = {}

                print('Loaded ips: %s/%s' % (count, lines))
        redis_db.zadd('ip_location:', ip_mapping)
        redis_db.hmset('location:', location_mapping)
        print('Loaded ips: %s/%s' % (count, lines))

    print('All done!')


if __name__ == '__main__':
    with app.app_context():
        load_ip_to_redis()
