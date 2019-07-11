# -*- coding: utf-8 -*-
"""
用户登录模块
"""

from flask import request
from flask_restful import Resource

from base.params import Param, parse_params
from base.response import RetDef, render_response
from app.services.user import (
    login_user, create_user, validate_user,
    logout_user, get_user
)
from app.views.common import logined


class UserResource(Resource):
    @parse_params(
        Param('username', required=True),
        Param('pwd', required=True)
    )
    def post(self):
        user = create_user(
            username=request.params['username'],
            pwd_md5=request.params['pwd']
        )
        if not user:
            return render_response(RetDef.USER_EXISTS)

        token = login_user(user)

        return render_response(
            data=user.to_json(),
            cookies={'token': token}
        )


class SessionResource(Resource):
    @logined
    def get(self):
        user = get_user(request.user_id)
        return render_response(data=user.to_json())

    @parse_params(
        Param('username', required=True),
        Param('pwd', required=True)
    )
    def post(self):
        user = validate_user(
            username=request.params['username'],
            pwd_md5=request.params['pwd']
        )
        if not user:
            return render_response(RetDef.USER_NOT_FOUND)

        token = login_user(user)

        return render_response(
            data=user.to_json(),
            cookies={'token': token}
        )

    @logined
    def delete(self):
        token = request.get_token()
        logout_user(token)

        return render_response()
