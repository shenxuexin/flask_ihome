# -*-coding:utf-8-*-

from . import api
from flask import request, g, jsonify, current_app
from ihome.util.commens import login_required
from ihome.response_code import RET
from ihome.models import User
from ihome.util.storage_image import storage
from ihome import db, constants
import re


@api.route('/users/avatar', methods=['POST'])
@login_required
def set_avatar():
    u'''
    参数: 图片(多媒体表单), user_id(g.user_id)
    :return:
    '''
    # 获取数据
    avatar = request.files.get('avatar')
    user_id = g.user_id

    # 校验数据
    if avatar is None:
        return jsonify(errno=RET.NODATA, errmsg=u'图片未上传')

    # 业务处理
    # 上传文件
    image_data = avatar.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=u'图片上传失败')

    # 保存文件路径
    try:
        user = User.query.filter_by(id=user_id).update({'avatar_url': file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'图片存储失败')

    # 返回响应
    avatar_url = constants.QINIU_URL_DOMIN + file_name
    return jsonify(errno=RET.OK, errmsg=u'上传成功', data={'avatar_url': avatar_url})


@api.route('/users/profile', methods=['GET'])
@login_required
def get_info():
    user_id = g.user_id
    user = User.query.get(user_id)

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg=u'用户不存在')

    avatar_url = constants.QINIU_URL_DOMIN + user.avatar_url
    data = {
        'username': user.name,
        'mobile': user.mobile,
        'avatar': avatar_url
    }
    return jsonify(errno=RET.OK, errmsg=u'查询成功', data=data)


@api.route('/users/auth', methods=['GET'])
@login_required
def get_auth():
    user_id = g.user_id

    user = User.query.get(user_id)
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg=u'用户不存在')

    data = {
        'real_name': user.real_name,
        'id_card': user.id_card
    }

    return jsonify(errno=RET.OK, errmsg=u'查询成功', data=data)


@api.route('/users/auth', methods=['POST'])
@login_required
def set_auth():
    u'''
    获取参数: real_name, id_card 格式:json
    :return:
    '''
    # 获取数据
    user_id = g.user_id
    real_name = request.form.get('real_name')
    id_card = request.form.get('id_card')

    # 数据校验
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数不完整')

    if not re.match(r'^[1-9]\d{7}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}$|^[1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X)$', id_card):
        return jsonify(errno=RET.PARAMERR, errmsg=u'身份证格式错误')

    # 业务处理: 存储认证信息
    try:
        User.query.filter_by(id=user_id).update({'real_name': real_name, 'id_card': id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'认证信息存储失败')

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'认证成功')

