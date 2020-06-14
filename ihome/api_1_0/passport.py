# -*-coding:utf-8-*-

from . import api
import re
from flask import request, jsonify, current_app, session
from ihome.response_code import RET
from ihome import redis_store, db
from ihome.models import User
from sqlalchemy.exc import IntegrityError


# POST /users
@api.route('/users', methods=['POST'])
def register():
    u'''
    参数: 手机号, sms_code, 密码, 重复密码
    参数格式: json
    :return:
    '''
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')
    repassword = req_dict.get('repassword')
    sms_code = req_dict.get('sms_code')

    # 参数校验
    if not all([mobile, password, repassword, sms_code]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'数据不完整')

    if not re.match(r'1[34578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=u'手机号格式错误')

    if password != repassword:
        return jsonify(errno=RET.PARAMERR, errmsg=u'两次密码不一致')

    # 业务处理
    # 从redis中取sms_code
    try:
        real_sms_code = redis_store.get('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'获取真实的手机验证码失败')

    # 判断是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg=u'手机验证码已过期')

    # 删除real_sms_code值
    redis_store.delete('sms_code_%s' % mobile)

    # 比较手机验证码
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg=u'手机验证码错误')

    # 注册用户
    user = User(name=mobile, mobile=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据回滚
        db.session.rollback()
        # 重复性错误: 手机号码已存在
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg=u'手机号码已存在')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库错误')

    # 记录登录状态
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'注册成功')

