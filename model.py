#!/usr/bin/env python
#coding:utf-8

from sqlalchemy import create_engine
from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from uuid import uuid1 as uuid
from config import Config
eng=create_engine(Config.db_string)
Model=declarative_base()
Session = sessionmaker(bind=eng)
session = Session()
class User(Model):
    __tablename__='users1'
    id=Column(String(32),primary_key=True)
    href=Column(String(255),nullable=False)
    content=Column(String(255),nullable=True)
    def __str__(self):
        return 'User<id={},href={},content={}>'.format(self.id,self.href,self.content)
    def save(self):
        if not self.id:
            self.id = uuid().hex
        session.add(self)
        session.commit()

class HouseDetail(Model):
    __tablename__ = 'house_detail'
    id=Column(String(32),primary_key=True)
    presale_num = Column(String(64),default="")
    building_num = Column(String(64))
    room_num = Column(String(64))
    floor_area = Column(String(64))
    use_area = Column(String(64))
    used_precent = Column(String(64))
    unit_price = Column(String(64))
    decorate_price = Column(String(64))
    total_price = Column(String(64))
    house_id = Column(String(32), Model.ForeignKey('houses.id'))
    def save(self):
        if not self.id:
            self.id = uuid().hex
        session.add(self)
        session.commit()


class Houses(Model):
    __tablename__ = 'houses'
    id = Column(String(32),primary_key=True)
    url = Column(String(255))
    name = Column(String(64))
    def save(self):
        if not self.id:
            self.id = uuid().hex
        session.add(self)
        session.commit()

if __name__=='__main__':
    pass
    # Model.metadata.drop_all(eng)
    # Model.metadata.create_all(eng)