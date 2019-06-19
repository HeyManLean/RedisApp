# -*- coding: utf-8 -*-
from flask import request, jsonify

from ad import ad_mod
from ad.services import add_ad, get_ad, remove_ad


@ad_mod.route('/', methods=['POST'])
def _add_ad():
    params = request.json
    data = add_ad(
        name=params.get('name'),
        desc=params.get('desc'),
        content=params.get('content'),
        locations=params.get('locations'),
        type=params.get('type'),
        value=params.get('value')
    )
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
