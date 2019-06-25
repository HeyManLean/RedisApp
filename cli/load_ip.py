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

    with open(filename,  encoding='utf-8', mode='r+') as fp:
        ip_mapping = {}
        location_mapping = {}

        temp_location = None
        temp_score = None
        temp_info = None

        count = 0
        lineno = 0
        for lineno, line in enumerate(fp):
            if not line:
                continue

            pieces = line.split(',')
            score = pieces[1]
            country, province, city = pieces[4:7]

            location = city or province or country

            if temp_location and location != temp_location:
                ip_mapping['%s_%s' % (temp_location, count)] = temp_score
                location_mapping[temp_location] = temp_info
                count += 1

                if not count % 10000:
                    redis_db.zadd('ip_location:', ip_mapping)
                    redis_db.hmset('location:', location_mapping)

                    ip_mapping = {}
                    location_mapping = {}

                    print('Loaded ips: %s/%s' % (lineno, lines))

            temp_location = location
            temp_score = score
            temp_info = '%s:%s:%s' % (country, province, city)

        ip_mapping['%s_%s' % (temp_location, count)] = temp_score
        location_mapping[temp_location] = temp_info
        redis_db.zadd('ip_location:', ip_mapping)
        redis_db.hmset('location:', location_mapping)
        print('Loaded ips: %s/%s' % (lineno, lines))

    print('All done!')


if __name__ == '__main__':
    with app.app_context():
        load_ip_to_redis()
