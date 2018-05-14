#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.common.pageHelper import PageResult
from app.models.Houses import Houses, HouseDetail
from app import db
import re

def get_house_name():
    houses = db.session.query(Houses).all()
    return {
        'data': [house.name for house in houses]
    }

def houses_list(limit=10, offset=0, keyword=None,build_num=0):
    query = db.session.query(HouseDetail)
    if keyword:
        keyword_string = re.sub(r"[\s+\.\!\/_,$%*^(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&（）]+'", "", keyword)
        house = Houses.query.filter(Houses.name.startswith(keyword_string)).first()
        if house:
            query = query.filter(HouseDetail.house==house.id)
        if build_num:
            query = query.filter(HouseDetail.building_num.startswith(build_num))
    return PageResult(query, limit, offset).to_dict(lambda house: {
        "id": house.id,
        "presale_num": house.presale_num,
        "building_num": house.building_num,
        "room_num": house.room_num,
        "floor_area": house.floor_area,
        "use_area": house.use_area,
        "used_precent": house.used_precent,
        "unit_price": house.unit_price,
        "decorate_price": house.decorate_price,
        "total_price": house.total_price,
        "house_name": house.houseinfo.name
    })