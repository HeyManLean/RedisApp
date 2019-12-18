#!/usr/bin/env python3
# coding=utf-8
from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, json, request


class Config:
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://web_dev:123456@localhost:4006/web_dev'
    # SQLALCHEMY_BINDS = {
    #     'web_dev': 'mysql+pymysql://web_dev:123456@localhost:3306/web_dev',
    #     'web_dev2': 'mysql+pymysql://web_dev:123456@localhost:3306/web_dev2',
    # }


class _JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if hasattr(o, 'to_dict'):
            return o.to_dict()

        return json.JSONEncoder.default(self, o)


app = Flask(__name__)
app.config.from_object(Config)
app.json_encoder = _JsonEncoder

db = SQLAlchemy()
db.init_app(app)


def model_to_dict(model, include_fields=None, exclude_fields=None):
    vo = {col.name: getattr(model, col.name) for col in model.__table__.columns}

    if include_fields:
        tmp_data = {}
        for field in include_fields:
            if field in vo:
                tmp_data[field] = vo[field]
        vo = tmp_data

    if exclude_fields:
        for field in exclude_fields:
            if field in vo:
                del(vo[field])

    return vo


db.Model.to_dict = model_to_dict


class User(db.Model):
    __tablename__ = 'users'
    # __bind_key__ = 'web_dev'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    fullname = db.Column(db.String(128))
    nickname = db.Column(db.String(32))

    addresses = db.relationship("Address", back_populates="user")

    create_time = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        vo = super().to_dict()
        vo['addresses'] = self.addresses
        return vo

    def __repr__(self):
        return "<User(name='%s', fullname='%s')>" % (
            self.name, self.fullname
        )


class Address(db.Model):
    __tablename__ = 'address'
    # __bind_key__ = 'web_dev2'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(62))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship("User", back_populates="addresses")


@app.route('/users')
def get_users():
    data = []

    for user in User.query.all():
        data.append(user.to_dict())

    return {
        'data': data,
        'bind_info': ''
    }


@app.route('/users/add')
def add_user():
    params = request.args
    user = User(
        name=params['name'],
        nickname=params['name'],
        fullname=params['name'])

    db.session.add(user)
    db.session.commit()

    return user.to_dict()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
