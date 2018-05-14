#!/usr/bin/env python
#coding:utf-8
from config import Config
def authorize(password,username):
    if username == Config.username and password == Config.password:
        return {
            'data': {
                'access_token': ''
            }
        }
    else:
        return {
            'data': '登录失败，用户密码错误'
        }