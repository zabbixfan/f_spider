#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.common.pageHelper import PageResult
from app.models.Houses import Houses, HouseDetail
from app import db
import re

def get_house_name():
    houses = db.session.query(Houses).all()
    return {
        'data': [{'name':house.name,'id':house.id} for house in houses]
    }
def get_building_num_by_house_name(id):
    build_nums = db.session.query(HouseDetail.building_num).filter(HouseDetail.house==id).group_by(HouseDetail.building_num).all()
    return {'data':[build[0]for build in build_nums]}

def get_building_by_name(id,build):
    rooms = db.session.query(HouseDetail).filter(HouseDetail.house==id).filter(HouseDetail.building_num==build).all()
    ret = []
    rooms.sort(key=lambda x:int(re.search(r'(\d+)室',x.room_num).group(1)))
    room_nums = sorted(list(set([re.search(r'(0\d)室',room.room_num).group(1) for room in rooms])))
    n = 0
    last = len(room_nums) - 1
    for index in range(len(rooms))[:-last:len(room_nums)]:
        m = 0
        for count in room_nums:
            if len(ret) < n+1:
                ret.append({})
            ret[n][count]='{}/{}/{}/{}'.format(rooms[index+m].room_num,rooms[index+m].floor_area,rooms[index+m].unit_price,rooms[index+m].total_price)
            m += 1
        n+=1
    return ret
def houses_list(limit=10, offset=0, keyword=None,build_num=0,area=0):
    query = db.session.query(HouseDetail)
    if keyword:
        keyword_string = re.sub(r"[\s+\.\!\/_,$%*^(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&（）]+'", "", keyword)
        house = Houses.query.filter(Houses.name.startswith(keyword_string)).first()
        if house:
            query = query.filter(HouseDetail.house==house.id)
        if build_num:
            query = query.filter(HouseDetail.building_num.startswith(build_num))
        if area:
            query = query.filter(HouseDetail.floor_area > area)
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