#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask
from redis import Redis


app = Flask(__name__)
redis_db = Redis(host='redis01', port=6379)


@app.route('/')
def index():
    key = 'show_me'

    redis_db.incr(key)
    value = redis_db.get(key)
    
    return 'I have been show for %s times!' % int(value)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
