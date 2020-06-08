# -*-coding:utf-8-*-

from . import api
from flask import current_app
from ihome import db


@api.route('/')
def index():
    # logging.debug('debug msg')
    current_app.logger.debug('flask debug test')
    return 'index page'