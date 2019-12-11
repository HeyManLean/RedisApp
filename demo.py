#!/usr/bin/env python3
# coding=utf-8

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine, event


engine = create_engine('mysql+pymysql://web_dev:123456@localhost:3306/web_dev',
                       pool_size=20, max_overflow=0)


@event.listens_for(engine, 'connect')
def receive_connect(dbapi_connection, connection_record):
    print('>>> dbapi_connection', dbapi_connection)
    print('>>> connection_record', connection_record)


connection = engine.connect()
result = connection.execute('select * from user;')
for item in result:
    print(item)

# connection.execute(
#     'insert into user(email, password, active, confirmed_at) '
#     'values("readonly@gmail.com", "123456", 1, now())')

connection.close()


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    create_time = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return "<User(name='%s', fullname='%s')>" % (
            self.name, self.fullname
        )


