# -*-coding:utf-8-*-

from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
from ihome.util import commens

# 数据库
db = SQLAlchemy()

# redis
redis_store = None

# 设置日志
# 日志记录级别
logging.basicConfig(level=logging.DEBUG)  # flask在debug环境下会忽略logging的级别,强行设置为DEBUG
# 创建日志记录器,指明存储路径,文件大小和数量
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024, backupCount=10)
# 日志记录格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d -- %(message)s')
# 记录器加载格式
file_log_handler.setFormatter(formatter)
# 添加日志记录器到全局
logging.getLogger().addHandler(file_log_handler)


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

    # 注册转换器
    app.url_map.converters['re'] = commens.ReConverter

    # 注册蓝图
    from . import api_1_0  # 延迟导入,避免循环引用
    app.register_blueprint(api_1_0.api, url_prefix='/api/v1.0')

    from ihome.web_html import html
    app.register_blueprint(html)

    return app