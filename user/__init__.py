# -*- coding: utf-8 -*-
"""
用户模块
"""
from flask import Blueprint

user_mod = Blueprint('user', __name__)

from user import views
