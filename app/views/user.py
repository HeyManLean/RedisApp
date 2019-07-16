# -*- coding: utf-8 -*-
"""
用户登录模块
"""

from flask import request
from flask_restful import Resource

from base.params import Param, parse_params
from base.response import StatusDef, render_response
from app.services.user import (
    login_user, create_user, validate_user,
    logout_user, get_user
)
from app.services.status import (
    follow_user, unfollow_user
)
from app.views.common import logined


class UserResource(Resource):
    @parse_params(
        Param('username', required=True),
        Param('pwd', required=True),
        Param('nickname', required=True),
    )
    def post(self):
        user = create_user(
            username=request.params['username'],
            pwd_md5=request.params['pwd'],
            nickname=request.params['nickname']
        )
        if not user:
            return render_response(StatusDef.USER_EXISTS)

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
            return render_response(StatusDef.USER_NOT_FOUND)

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


class FriendsResource(Resource):
    @logined
    @parse_params(
        Param('other_uid', type=int, required=True)
    )
    def post(self):
        ret = follow_user(request.user_id, request.params['other_uid'])
        if not ret:
            return render_response(StatusDef.USER_LIKED)
        else:
            return render_response()

    @logined
    @parse_params(
        Param('other_uid', type=int, required=True)
    )
    def delete(self):
        ret = unfollow_user(request.user_id, request.params['other_uid'])
        if not ret:
            return render_response(StatusDef.USER_UNLIKED)
        else:
            return render_response()
