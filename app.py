#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask
from redis import Redis
import pymongo
# import pymysql


def create_app():
    app = Flask(__name__)

    from ad import ad_mod

    app.register_blueprint(ad_mod, url_prefix='/ads ')

    @app.route('/')
    def index():
        key = 'show_me'

        redis_db.incr(key)
        value = redis_db.get(key)

        return 'I have been show for %s times!' % int(value)

    return app


redis_host = 'localhost'  # 'redis'
mongo_host = 'localhost'  # 'mongo
redis_db = Redis(host=redis_host, port=6379, decode_responses=True)
mongo_db = pymongo.MongoClient(host=mongo_host, port=27017)['my_app']
# mysql_db = pymysql.connect(host='mysql', port=3306, user='root', password='123456')
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
