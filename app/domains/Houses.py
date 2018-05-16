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
    builds = db.session.query(HouseDetail.building_num).filter(HouseDetail.house==id).group_by(HouseDetail.building_num).all()
    build_nums = set([re.match('\d+',build[0]).group() for build in builds])
    return {'data':list(build_nums)}

def get_building_by_name(id,build):

    ret = []
    #过滤那些特殊楼幢
    builds = db.session.query(HouseDetail.building_num,db.func.count(HouseDetail.building_num)).filter(HouseDetail.house==id).filter(HouseDetail.building_num.startswith(build)).group_by(HouseDetail.building_num).all()
    max = 0
    for i in builds:
        if i[1] > max:
            max = i[1]
    unit_nums = [build[0]for build in builds if build[1] == max]

    #获取楼幢号和房号
    rooms = HouseDetail.query.filter(HouseDetail.house == id).filter(HouseDetail.building_num.in_(unit_nums)).all()
    rooms.sort(key=lambda x: int(re.search(r'(\d+)室', x.room_num).group(1)))
    room_nums = sorted(list(set([re.search(r'(\d\d)室', room.room_num).group(1) for room in rooms])))

    cloumn_name = [unit + room for unit in unit_nums for room in room_nums]
    floors = sorted(list(set([int(re.search(r'^(\d+)\d\d室', room.room_num).group(1)) for room in rooms])))
    #根据楼层循环
    for floor in floors:
        data = {}
        for m in unit_nums:
            for n in room_nums:
                for index,room in enumerate(rooms):
                    if room.building_num == m and room.room_num.startswith(str(floor)+n):
                        data['{}{}'.format(m,n)] = '{},{},单价{},总价:{}'.format(room.room_num,room.floor_area,int(room.unit_price),int(room.total_price))
                        rooms.pop(index)
                        break
                else:
                    data['{}{}'.format(m, n)] = ''
        ret.append(data)
    return {'cloumns': cloumn_name,'detail': ret}

def houses_list(limit=10, offset=0, keyword=None,build_num=0,area=0):
    query = db.session.query(HouseDetail)
    if keyword:
        keyword_string = re.sub(r"[\s+\.\!\/_,$%*^(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&（）]+'", "", keyword)
        query = query.filter(HouseDetail.house==keyword_string)
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