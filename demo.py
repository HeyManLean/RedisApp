#!/usr/bin/env python3
# coding=utf-8
import logging
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    create_engine, event,
    Column, Integer, String, DateTime, ForeignKey
)
from sqlalchemy.orm import sessionmaker, relationship
from flask_sqlalchemy import SQLAlchemy


engine = create_engine('mysql+pymysql://web_dev:123456@localhost:3306/web_dev',
                       pool_size=20, max_overflow=0, echo=True)


@event.listens_for(engine, 'connect')
def receive_connect(dbapi_connection, connection_record):
    print('>>> dbapi_connection', dbapi_connection)
    print('>>> connection_record', connection_record.connection)


connection = engine.connect()
result = connection.execute('select * from user;')
for item in result:
    print(item)

# connection.execute(
#     'insert into user(email, password, active, confirmed_at) '
#     'values("readonly@gmail.com", "123456", 1, now())')


connection.close()


Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    """
    ```sql
        CREATE TABLE users (
            id INTEGER NOT NULL AUTO_INCREMENT,
            name VARCHAR(32),
            fullname VARCHAR(128),
            nickname VARCHAR(32),
            create_time DATETIME,
            PRIMARY KEY (id)
        )
    ```
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    fullname = Column(String(128))
    nickname = Column(String(32))

    addresses = relationship("Address", back_populates="user")

    create_time = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return "<User(name='%s', fullname='%s')>" % (
            self.name, self.fullname
        )


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    email = Column(String(62))
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="addresses")


print('>>> User.__table__')
print(repr(User.__table__))


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


first_user = User(name='lean', fullname='heymanlean', nickname='lean')
address = Address(email='heymanlean@gmail.com')
first_user.addresses.append(address)
print(first_user.name)

session.add(first_user)
print('>>> session.dirty, session.new')
print(session.dirty, session.new)

session.flush()
print('>>> session.dirty, session.new')
print(session.dirty, session.new)
# session.rollback()
session.commit()
