#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import api
from flask import g,jsonify,request
from flask_restful import Resource, reqparse,inputs
from ..common.ApiResponse import ApiResponse, ResposeStatus
from flasgger import swag_from
from app.common.api_doc_helper import get_request_parser_doc_dist
from app.domains.Houses import houses_list, get_house_name
from app.common.AuthenticateDecorator import need_user

def get_args(return_parse_args=True):

    rp = reqparse.RequestParser()
    rp.add_argument('username',default="")
    rp.add_argument('password',default="")
    return rp.parse_args() if return_parse_args else rp


class Login(Resource):


    @swag_from(get_request_parser_doc_dist("login", ["login"], get_args(False)))
    def get(self):
        args = get_args()
        return ApiResponse(authorize(keyword=args.keyword,offset=args.offset,limit=args.limit,build_num=args.build_num))