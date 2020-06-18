# -*-coding:utf-8-*-

from flask import Blueprint

api = Blueprint('api_v_1.0', __name__)

from . import demo
from . import verify_code, passport, profile