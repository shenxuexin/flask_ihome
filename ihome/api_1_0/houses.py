# -*-coding:utf-8-*-

from . import api
import json
from flask import current_app, jsonify, g, request
from ihome.response_code import RET
from ihome.models import Area, House, Facility, HouseImage
from ihome import redis_store, constants, db
from ihome.util.commens import login_required
from ihome.util.storage_image import storage


@api.route('/areas', methods=['GET'])
def get_areas():
    # 查询缓存
    try:
        ret_json = redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if ret_json is not None:
            current_app.logger.info('hit redis cache: area_info')
            return ret_json, 200, {'Content-Type': 'application/json'}

    # 查询数据库, 获取城区信息
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库错误')

    # 将对象转化为字典
    area_dict_li = []
    for area in area_li:
        area_dict_li.append(area.to_dict())

    # 转化为json
    ret_dict = dict(errno=RET.OK, errmsg='OK', data=area_dict_li)
    ret_json = json.dumps(ret_dict)

    # 存储到缓存
    try:
        redis_store.setex('area_info', constants.AREA_INFO_REDIS_CACHE_EXPIRE, ret_json)
    except Exception as e:
        current_app.logger.error(e)

    return ret_json, 200, {'Content-Type': 'application/json'}


@api.route('/houses/info', methods=['POST'])
@login_required
def save_house_info():
    u'''
    参数
    user_id
    area_id
    title
    price
    address
    room_count
    acreage
    unit
    capacity
    beds
    deposit
    min_days
    max_days
    facilities: ['1', '2']
    :return:
    '''
    # 获取数据
    user_id = g.user_id
    req_dict = request.get_json()
    area_id = req_dict.get('area_id')
    title = req_dict.get('title')
    price = req_dict.get('price')
    address = req_dict.get('address')
    room_count = req_dict.get('room_count')
    acreage = req_dict.get('acreage')
    unit = req_dict.get('unit')
    capacity = req_dict.get('capacity')
    beds = req_dict.get('beds')
    deposit = req_dict.get('deposit')
    min_days = req_dict.get('min_days')
    max_days = req_dict.get('max_days')

    # 校验数据
    if not all([area_id, title, price, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数不完整')

    try:
        price = int(float(price)*100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数错误')

    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库错误')

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg=u'城区不存在')

    try:
        room_count = int(room_count)
        acreage = int(acreage)
        capacity = int(capacity)
        min_days = int(min_days)
        max_days = int(max_days)
    except Exception as e:
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数错误')

    if room_count<0 or acreage<0 or capacity<0 or min_days<0 or max_days<0:
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数错误')

    # 业务处理
    house = House()
    house.user_id = user_id,
    house.area_id = area_id,
    house.title = title,
    house.price = price,
    house.address = address,
    house.room_count = room_count,
    house.acreage = acreage,
    house.unit = unit,
    house.capacity = capacity,
    house.beds = beds,
    house.deposit = deposit,
    house.min_days = min_days,
    house.max_days = max_days

    try:
        db.session.add(house)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库异常')

    # 添加设备
    facility_ids = req_dict.get('facility')
    if facility_ids is not None:
        try:
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg=u'设备信息存储失败')

        if facilities:
            house.facilities = facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=u'发布房源失败')

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'发布成功', data={'house_id': house.id})


@api.route('/houses/image', methods=['POST'])
@login_required
def set_house_image():
    # 获取数据: image, house_id
    image_file = request.files.get('house_image')
    house_id = request.form.get('house_id')

    # 数据校验
    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'数据不完整')

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库异常')

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg=u'房屋不存在')

    # 业务处理
    image_data = image_file.read()
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=u'上传图片失败')

    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = file_name
    db.session.add(house_image)

    if not house.index_image_url:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'图片存储失败')

    # 返回响应
    image_url = constants.QINIU_URL_DOMIN+file_name
    return jsonify(errno=RET.OK, errmsg=u'保存成功', data={'image_url': image_url})