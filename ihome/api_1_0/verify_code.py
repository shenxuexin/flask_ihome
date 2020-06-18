# -*-coding:utf-8-*-

from . import api
from ihome.util.captcha.captcha import captcha
from ihome import redis_store, db, constants
from ihome.response_code import RET
from ihome.models import User
from flask import current_app, jsonify, make_response, request
# from ihome.tasks.send_sms import send_sms
from ihome.tasks.sms.tasks import send_sms
import random


# GET /image_code/<image_code_id>
@api.route('/image_code/<image_code_id>')
def get_image_code(image_code_id):
    u'''
    获取图片验证码
    :param image_code_id: 前端生成的图片编码
    :return: 正常:image, 异常:json
    '''
    # 业务逻辑处理
    # 生成图片
    name, text, image = captcha.generate_captcha()

    # 存入redis: 图片真实文本和编号,采用键值对的方式存储
    # redis_store.set('image_%s' % image_code_id, text)
    # redis_store.expire('image_%s' % image_code_id, 180)
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRE, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        # 返回错误信息
        data = {
            'errno': RET.DBERR,
            'errmsg': 'cannot save image code in redis'
        }
        return jsonify(**data)

    # 返回图片
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'

    return resp


# GET /sms_code/<mobile>?image_code=xxx&image_code_id=xxx
@api.route('/sms_code/<re(r"1[34578]\d{9}"):mobile>')
def get_sms_code(mobile):
    # 获取数据
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')

    # 数据校验
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数不完整')

    # 业务处理
    # 获取图片验证码真实值
    try:
        real_image_code = redis_store.get('image_code_%s'%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'redis连接错误')

    # 判断图片验证码是否过期
    if real_image_code is None:
        return jsonify(errno=RET.DATAERR, errmsg=u'图片验证码已过期')

    # 删除redis中的图片验证码
    try:
        redis_store.delete('image_code_%s'%image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 比较图片验证码是否相符
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg=u'图片验证码错误')

    # 判断60s内是否获取过验证码
    try:
        send_flag = redis_store.get('send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR, errmsg=u'请求过于频繁,请60s后重试')

    # 判断手机号是否已存在
    try:
        user = User.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg=u'用户已存在')

    # 生成手机号验证码
    sms_code = '%06d' % random.randint(0, 999999)

    # 保存手机验证码
    try:
        redis_store.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRE, sms_code)
        # 保存该手机60s内访问过的标记
        redis_store.setex('send_sms_code_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg=u'手机验证码保存失败')

    # 发送手机验证码
    # try:
    #     ccp = CCP()
    #     ret = ccp.send_temp_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRE / 60)], 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg=u'手机验证码发送异常')

    # 利用celery发送短信
    send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRE / 60)], 1)

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'发送成功')
