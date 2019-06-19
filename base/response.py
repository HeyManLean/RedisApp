# -*- coding: utf-8 -*-
"""
自定义响应
"""
from collections import abc

from flask import jsonify


def render_response(obj):
    if isinstance(obj, abc.Mapping):
        return jsonify(obj)

    return jsonify(obj.to_dict())
