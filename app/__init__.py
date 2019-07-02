# -*- coding: utf-8 -*-
import logging
# import os

from flask import Flask
from redis import Redis
import pymongo

from base import MyRequest
from base.errors import ParamError
from base.response import render_response


redis_host = 'localhost'  # 'redis'
mongo_host = 'localhost'  # 'mongo
redis_db = Redis(host=redis_host, port=6379, decode_responses=True)
mongo_db = pymongo.MongoClient(host=mongo_host, port=27017)['my_app']


def create_app():
    app = Flask(__name__)
    app.request_class = MyRequest

    from . import views
    views.init_app(app)

    @app.route('/')
    def index():
        key = 'show_me'
        redis_db.incr(key)
        value = redis_db.get(key)
        return 'I have been show for %s times!' % int(value)

    @app.errorhandler(ParamError)
    def handle_param_error(error):
        retcode = error.retcode
        logging.info(retcode.to_dict())
        return render_response(retcode)

    return app
