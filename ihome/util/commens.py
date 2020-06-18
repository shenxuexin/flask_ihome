# -*-coding:utf-8-*-

from werkzeug.routing import BaseConverter
import functools
from flask import session, jsonify, g
from ihome.response_code import RET


# 转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        super(ReConverter, self).__init__(url_map)
        self.regex = regex


# 登录校验装饰器
def login_required(view_func):
    @functools.wraps(view_func)   # 将wrapper的__doc__, __name__等属性更改为view_func的属性值
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is not None:
            g.user_id = user_id   # g为全局上下文
            return view_func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg=u'用户未登录')
    return wrapper