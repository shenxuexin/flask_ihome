# -*-coding:utf-8-*-

from redis import StrictRedis


class Config(object):
    '''配置文件'''
    SECRET_KEY = 'haksdIDHWEIUHAsJAJDFHAA7hkuHKJML54a2sd4a'

    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:199741833@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = '192.168.153.131'
    REDIS_PORT = 6379

    # redis-session
    PERMANENT_SESSION_LIFETIME = 604800  # 保存时间设置为一周
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True  # 利用cookie保存sessionid
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


class DevelopConfig(Config):
    '''开发环境下的配置'''
    DEBUG = True


class ProductionConfig(Config):
    '''生产环境下的配置'''
    pass


config_map = {
    'develop': DevelopConfig,
    'product': ProductionConfig
}