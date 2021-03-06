#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
import logging
from celery import Celery

import config
celery = Celery(__name__,broker=config.Config.CELERY_BROKER_URL)
db = SQLAlchemy()

def logger_init(name="root"):
    """
    log 初始化
    :param name:
    :return:
    """
    logger = logging.getLogger(name)
    handler = logging.FileHandler('app.log', encoding='utf-8')
    logging_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s"
    )
    handler.setFormatter(logging_format)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def logger(name="root"):
    """
    日志 logger
    :param name:
    :return:
    """
    return logging.getLogger(name)


def create_app():
    import app.api
    app = Flask(__name__, instance_relative_config=True)
    # 注册配置文件
    app.config.from_object(config.Config)
    celery.conf.update(app.config)
    # SQLAlchemy
    db.init_app(app)
    # 注册 Blueprint
    # 注册 Api
    api.api.init_app(app)
    # CORS
    CORS(app, resources={r"*": {"origins": config.Config.CORS_ORIGINS}})
    # LOG
    logger_init()
    Swagger(app)
    return app