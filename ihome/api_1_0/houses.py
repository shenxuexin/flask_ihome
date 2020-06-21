# -*-coding:utf-8-*-

from . import api
import json
from flask import current_app, jsonify, g, request, session
from ihome.response_code import RET
from ihome.models import Area, House, Facility, HouseImage, User, Order
from ihome import redis_store, constants, db
from ihome.util.commens import login_required
from ihome.util.storage_image import storage
from datetime import datetime


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


@api.route('/user/houses', methods=['GET'])
@login_required
def get_user_houses():
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库错误')

    houses_li = []
    for house in houses:
        houses_li.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg=u'查询成功', data=houses_li)


@api.route('/houses/index', methods=['GET'])
def get_houses_index():
    try:
        cache_data = redis_store.get('houses_index')
    except Exception as e:
        current_app.logger.error(e)
        cache_data = None

    if cache_data:
        current_app.logger.info('hit redis cache: houses_index')
        response = '{"errno": "%s", "errmsg": "%s", "data": %s}' % (RET.OK, u'查询成功', cache_data)

        return response, 200, {'Content-Type': 'application/json'}

    try:
        houses = House.query.order_by(House.order_count.desc()).limit(constants.HOME_SHOW_HOUSES_NUM)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库错误')

    if not houses:
        return jsonify(errno=RET.NODATA, errmsg=u'查询无数据')

    houses_li = []
    for house in houses:
        if not house.index_image_url:
            continue
        houses_li.append(house.to_basic_dict())

    houses_li = json.dumps(houses_li)
    try:
        redis_store.setex('houses_index', constants.HOME_HOUSES_REDIS_EXPIRE, houses_li)
    except Exception as e:
        current_app.logger.error(e)

    response = '{"errno": "%s", "errmsg": "%s", "data": %s}' % (RET.OK, u'查询成功', houses_li)
    return response, 200, {'Content-Type': 'application/json'}


@api.route('/houses/<int:house_id>', methods=['GET'])
def get_house_info(house_id):
    user_id = session.get('user_id', -1)

    try:
        cache_data = redis_store.get('house_info_%s' % house_id)
    except Exception as e:
        current_app.logger.error(e)
        cache_data = None

    if cache_data:
        current_app.logger.info('hit redis cache: house_info_%s' % house_id)
        resp = '{"errno":"%s","errmsg":"%s","data":{"user_id": %s,"house":%s}}' \
                   % (RET.OK, u'查询成功', user_id, cache_data)

        try:
            json.loads(resp)
        except Exception as e:
            print('='*50)
            print(e)

        return resp, 200, {'Content-Type': 'application/json'}

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库错误')

    house_dict = house.to_full_dict()
    house_json = json.dumps(house_dict)

    try:
        redis_store.setex('house_info_%s' % house_id, constants.HOUSE_INFO_REDIS_EXPIRE, house_json)
    except Exception as e:
        current_app.logger.errpr(e)

    resp = '{"errno": "%s", "errmsg": "%s", "data": {"user_id": "%s", "house":"%s"}}' \
               % (RET.OK, u'查询成功', user_id, house_json)

    return resp, 200, {'Content-Type': 'application/json'}


# /api/v1.0/houses/?aid=1&sd=2020-5-20&ed=2020-5-21&sk="new"&page=5
@api.route('/houses', methods=['GET'])
def get_house_list():
    # 获取参数
    area_id = request.args.get('aid', '')
    start_date = request.args.get('sd', '')
    end_date = request.args.get('ed', '')
    sort_key = request.args.get('sk', 'new')
    page = request.args.get('page')
    print('params: %s--%s--%s--%s' % (area_id, start_date, end_date, sort_key))

    # 参数校验
    # 校验日期
    try:
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=u'日期参数错误')

    # 校验页码
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    if page <= 0:
        page = 1

    # 校验区域
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=u'区域格式错误')

    # 业务处理: 查询并返回满足条件的房屋数据
    # 查询缓存
    try:
        redis_key = 'houses_list_%s_%s_%s_%s' % (start_date, end_date, area_id, sort_key)
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            current_app.logger.info('hit redis cache: %s' % redis_key)
            return resp_json, 200, {'Content-Type': 'application/json'}

    # 构造房屋查询条件列表容器
    filter_params = []

    # 构造时间条件
    conflict_orders = None
    if start_date and end_date:
        conflict_orders = Order.query.filter(Order.begin_date < end_date and Order.end_date > start_date).all()
    elif start_date:
        conflict_orders = Order.query.filter(Order.end_date > start_date).all()
    elif end_date:
        conflict_orders = Order.query.filter(Order.begin_date < end_date).all()

    if conflict_orders is not None:
        conflict_ids = [order.id for order in conflict_orders]
        filter_params.append(House.id.notin_(conflict_ids))

    # 构造区域条件
    print(area_id)
    if area_id:
        filter_params.append(House.area_id==area_id)

    # 查询房屋数据
    if sort_key == 'booking':
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == 'price-inc':
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == 'price-des':
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 分页
    try:
        paginator = house_query.paginate(page=page, per_page=constants.PER_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'数据库错误')

    houses = []
    for house in paginator.items:
        houses.append(house.to_basic_dict())

    total_page_num = paginator.pages

    resp_data = dict(errno=RET.OK, errmsg=u'查询成功', data={'houses': houses, 'total_page': total_page_num, 'current_page': page})
    resp_json = json.dumps(resp_data)

    # 添加缓存
    if page <= total_page_num:
        redis_key = 'houses_list_%s_%s_%s_%s' % (start_date, end_date, area_id, sort_key)
        redis_store.hset(redis_key, page, resp_json)
        redis_store.expire(redis_key, constants.HOUSE_LIST_REDIS_CACHE_EXPIRE)

    return resp_json, 200, {'Content-Type': 'application/json'}
