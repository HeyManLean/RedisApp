# -*- coding: utf-8 -*-
"""
广告定向模块
"""
from flask import request
from flask_restful import Resource

from app.services.ad import (
    add_ad, get_ad, remove_ad, record_click,
    target_ads, ip_to_location
)
from base.params import Param, parse_params
from base.response import render_response


class AdResource(Resource):
    @parse_params(
        Param('content', required=True)
    )
    def get():
        locations = []
        loc = ip_to_location('59.42.120.121' or request.ip)
        if loc:
            locations.append(loc)

        target_id, ad_id = target_ads(locations, request.params['content'])
        ad = get_ad(ad_id)
        data = ad.to_json()

        return render_response(
            data={
                'target_id': target_id,
                'data': data
            })

    @parse_params(
        Param('name', required=True),
        Param('type', choices=('cpa', 'cpc', 'cpm'), default='cpm'),
        Param('value', type=float, required=True),
        Param('content', required=True),
        Param('locations', type=list, required=True),
    )
    def post(self):
        data = add_ad(**request.params)
        return render_response(data=data)


class SingleAdResource(Resource):
    def get(self, ad_id):
        ad = get_ad(ad_id)
        data = ad.to_json()
        return render_response(data=data)

    @parse_params(
        Param('action', choices=('click', 'action'), default='click')
    )
    def post(self, ad_id):
        data = record_click(**request.params)
        return render_response(data=data)

    def delete(self, ad_id):
        remove_ad(ad_id)
        return render_response()
