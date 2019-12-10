#!/usr/bin/env python3
# coding=utf-8

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

connection.close()
