# -*- coding: utf-8 -*-
from flask import request, jsonify

from ad import ad_mod
from ad.services import add_ad, get_ad, remove_ad
from base import Argument, parse_args


@ad_mod.route('/add', methods=['POST'])
@parse_args(
    Argument('name', required=True),
    Argument('type', choices=('cpa', 'cpc', 'cpm'), default='cpm'),
    Argument('value', type=float, required=True),
    Argument('content', required=True),
    Argument('locations', type=list, required=True),
)
def _add_ad():
    data = add_ad(**request.params)
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
@parse_args(
    Argument('name', default='ABC', choices=('ABC', 'abc'), required=True),
    Argument('age', type=int, help='age: (1, 100)', required=True)
)
def test():
    params = request.params
    return jsonify(params)
