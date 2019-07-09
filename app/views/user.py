# -*- coding: utf-8 -*-
"""
用户登录模块
"""

from flask import Blueprint, request

from base.params import Param, parse_params
from base.response import RetDef, render_response
from app.services.user import (
    login_user, create_user, validate_user,
    logout_user, get_user
)
from app.views.common import logined


user_mod = Blueprint('user', __name__)


@user_mod.route('/signup', methods=['POST'])
@parse_params(
    Param('username', required=True),
    Param('pwd', required=True),
)
def signup():
    user = create_user(
        username=request.params['username'],
        pwd_md5=request.params['pwd']
    )
    if not user:
        return render_response(RetDef.USER_EXISTS)

    token = login_user(user)

    return render_response(
        RetDef.SUCCESS,
        data=user.to_json(),
        cookies={'token': token}
    )


@user_mod.route('/signin', methods=['POST'])
@parse_params(
    Param('username', required=True),
    Param('pwd', required=True)
)
def signin():
    """用户登录"""
    user = validate_user(
        username=request.params['username'],
        pwd_md5=request.params['pwd']
    )
    if not user:
        return render_response(RetDef.USER_NOT_FOUND)

    token = login_user(user)

    return render_response(
        RetDef.SUCCESS,
        data=user.to_json(),
        cookies={'token': token}
    )


@user_mod.route('/signout', methods=['POST'])
@logined
def signout():
    """用户注销"""
    token = request.get_token()
    logout_user(token)

    return render_response(RetDef.SUCCESS)


@user_mod.route('/session')
@logined
def check_session():
    """检验登录态"""
    user = get_user(request.user_id)
    return render_response(
        RetDef.SUCCESS,
        data=user.to_json()
    )
