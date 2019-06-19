# -*- coding: utf-8 -*-
"""
广告定向模块
"""
from flask import Blueprint

ad_mod = Blueprint('ad', __name__)

from ad import views
