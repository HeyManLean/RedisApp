# -*- coding: utf-8 -*-
"""
用户登录模块
"""

from flask import Blueprint, request

from base import Param, parse_params
from base.response import RetDef, render_response
from app.services.user import login_user, create_user, validate_user


user_mod = Blueprint('user', __name__)


@user_mod.route('/signup', methods=['POST'])
@parse_params(
    Param('username', required=True),
    Param('pwd', required=True),
)
def _signup_user():
    user = create_user(
        username=request.params['username'],
        pwd_md5=request.params['pwd_md5']
    )
    if not user:
        return render_response(RetDef.USER_EXISTS)

    token = login_user(user)
    request.token = token

    return render_response(RetDef.SUCCESS, data=user.to_json())


@user_mod.route('/signin', methods=['POST'])
@parse_params(
    Param('username', required=True),
    Param('pwd', required=True)
)
def _signin_user():
    """用户登录"""
    user = validate_user(
        username=request.params['username'],
        pwd_md5=request.params['pwd']
    )
    if not user:
        return render_response(RetDef.SIGNIN_FAILED)

    token = login_user(user)
    request.token = token

    return render_response(RetDef.SUCCESS, data=user.to_json())
