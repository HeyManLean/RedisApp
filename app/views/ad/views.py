# -*- coding: utf-8 -*-
from flask import request, jsonify

from app.views.ad import ad_mod
from app.services.ad import (
    add_ad, get_ad, remove_ad, record_click,
    target_ads, ip_to_location
)
from base import Param, parse_params


@ad_mod.route('/add', methods=['POST'])
@parse_params(
    Param('name', required=True),
    Param('type', choices=('cpa', 'cpc', 'cpm'), default='cpm'),
    Param('value', type=float, required=True),
    Param('content', required=True),
    Param('locations', type=list, required=True),
)
def _add_ad():
    data = add_ad(**request.params)
    return jsonify(data)


@ad_mod.route('/target', methods=['POST'])
@parse_params(
    Param('content', required=True)
)
def _target_ads():
    locations = []
    loc = ip_to_location('59.42.120.121' or request.ip)
    if loc:
        locations.append(loc)

    target_id, ad_id = target_ads(locations, request.params['content'])
    ad = get_ad(ad_id)
    data = ad.to_json()

    return jsonify({
        'target_id': target_id,
        'data': data
    })


@ad_mod.route('/click', methods=['POST'])
@parse_params(
    Param('target_id', required=True),
    Param('ad_id', required=True),
)
def _click_ad():
    data = record_click(**request.params)
    return jsonify(data)


@ad_mod.route('/<string:ad_id>')
def _get_ad(ad_id):
    ad = get_ad(ad_id)
    data = ad.to_json()
    return jsonify(data)


@ad_mod.route('/<string:ad_id>', methods=['DELETE'])
def _remove_ad(ad_id):
    remove_ad(ad_id)
    return jsonify({})


@ad_mod.route('/test')
@parse_params(
    Param('name', default='ABC', choices=('ABC', 'abc'), required=True),
    Param('age', type=int, help='age: (1, 100)', required=True)
)
def test():
    params = request.params
    return jsonify(params)
