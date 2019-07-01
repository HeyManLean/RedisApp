# -*- coding: utf-8 -*-
import logging
# import os

from flask import Flask
from redis import Redis
import pymongo
# import pymysql

from base import MyRequest
from base.errors import ParamError
from base.response import render_response


# dirpath = os.path.abspath(os.path.dirname(__file__))
# logging.basicConfig(
#     level=logging.DEBUG,
#     filename=os.path.join(dirpath, 'app.log'),
#     filemode='a+',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     format='[%(levelname)s][%(lineno)s] %(asctime)s - %(message)s'
# )

redis_host = 'localhost'  # 'redis'
mongo_host = 'localhost'  # 'mongo
redis_db = Redis(host=redis_host, port=6379, decode_responses=True)
mongo_db = pymongo.MongoClient(host=mongo_host, port=27017)['my_app']


def create_app():
    app = Flask(__name__)
    app.request_class = MyRequest

    from app.ad import ad_mod
    app.register_blueprint(ad_mod, url_prefix='/ads')

    @app.route('/')
    def index():
        key = 'show_me'
        redis_db.incr(key)
        value = redis_db.get(key)
        return 'I have been show for %s times!' % int(value)

    @app.errorhandler(ParamError)
    def handle_param_error(error):
        logging.info(error.to_dict())
        return render_response(error)

    return app
# -*- coding: utf-8 -*-
"""
视图模块
"""
from app.views.ad import ad_mod
from app.views.ad import views
