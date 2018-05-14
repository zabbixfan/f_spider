#!/usr/bin/env python
#coding:utf-8

from sqlalchemy import create_engine
from sqlalchemy import Column,Integer,String,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy import ForeignKey
from uuid import uuid1 as uuid
from config import Config
eng=create_engine(Config.db_string)
Model=declarative_base()
Session = sessionmaker(bind=eng)
session = Session()


class HouseDetail(Model):
    __tablename__ = 'house_detail'
    id=Column(String(32),primary_key=True)
    presale_num = Column(String(64),default="")
    building_num = Column(String(64))
    room_num = Column(String(64))
    floor_area = Column(Float)
    use_area = Column(Float)
    used_precent = Column(Float)
    unit_price = Column(Float)
    decorate_price = Column(Float)
    total_price = Column(Float)
    house = Column(String(32),ForeignKey('houses.id'))
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
    details = relationship('HouseDetail',backref='houseinfo')
    def save(self):
        if not self.id:
            self.id = uuid().hex
        session.add(self)
        session.commit()

if __name__=='__main__':
    Model.metadata.drop_all(eng)
    Model.metadata.create_all(eng)
    pass