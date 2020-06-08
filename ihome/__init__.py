# -*-coding:utf-8-*-

from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf import CSRFProtect

# 数据库
db = SQLAlchemy()

# redis
redis_store = None


# 工厂模式
def create_app(config_name):
    '''
    create app
    :param config_name: str ('develop', 'product')
    :return: app
    '''
    app = Flask(__name__)
    config_obj = config_map.get(config_name)
    app.config.from_object(config_obj)

    # 初始化数据库连接
    db.init_app(app)

    # 初始化redis
    global redis_store
    redis_store = StrictRedis(host=config_obj.REDIS_HOST, port=config_obj.REDIS_PORT)

    # redis-session
    Session(app)

    # 设置csrf校验
    CSRFProtect(app)

    # 注册蓝图
    from . import api  # 延迟导入,避免循环引用
    app.register_blueprint(api.api, url_prefix='/api/v1.0')

    return app