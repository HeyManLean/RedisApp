# -*- coding: utf-8 -*-
from flask import request
from flask_restful import Resource

from base.params import Param, parse_params
from base.response import render_response, StatusDef
from app.services.status import (
    post_status, delete_status, get_status_contents
)
from app.views.common import logined


class StatusesResource(Resource):
    @logined
    @parse_params(
        Param('timeline', choices=('home', 'profile'), default='home'),
        Param('page', type=int, default=1),
        Param('count', type=int, default=10)
    )
    def get(self):
        statuses = get_status_contents(
            request.user_id,
            **request.params
        )
        return render_response(data=statuses)

    @logined
    @parse_params(
        Param('content', required=True)
    )
    def post(self):
        ret = post_status(request.user_id, request.params['content'])
        if not ret:
            return render_response(StatusDef.STATUS_CREATE_FAIL)
        else:
            return render_response()


class StatusResource(Resource):
    @logined
    def delete(self, status_id):
        ret = delete_status(request.user_id, status_id)
        if not ret:
            return render_response(StatusDef.STATUS_DELETE_FAIL)
        else:
            return render_response()
