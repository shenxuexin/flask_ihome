# -*-coding:utf-8-*-

from . import api
from ihome.util.commens import login_required
from flask import request, g, jsonify, current_app
from ihome.response_code import RET
from datetime import datetime
from ihome.models import Order, House
from ihome import db, redis_store


@api.route('/orders', methods=['POST'])
@login_required
def save_orders():
    # 获取数据
    user_id = g.user_id
    req_dict = request.get_json()
    print(req_dict)
    house_id = req_dict.get('house_id')
    start_date_str = req_dict.get('start_date')
    end_date_str = req_dict.get('end_date')

    # 数据校验
    # 数据完整性
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg=u'数据不完整')

    # 校验时间格式
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        assert start_date <= end_date

        # 提取入住天数
        days = (end_date-start_date).days + 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=u'时间格式错误')

    # 校验房屋
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'房屋信息查询失败')

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg=u'房屋不存在')

    # 校验入住时间冲突
    try:
        order_count = Order.query.filter(start_date<Order.end_date, house_id==house_id,
                                         end_date>Order.begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'入住时间校验出错')

    if order_count > 0:
        return jsonify(errno=RET.DATAEXIST, errmsg=u'订单冲突')

    # 校验房主和下单者
    if house.user_id == user_id:
        return jsonify(errno=RET.ROLEERR, errmsg=u'房主不允许下单')

    # 业务处理: 保存订单
    order = Order()
    order.user_id = user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = days * house.price

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'订单保存失败')

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'下单成功')


# /api/v1.0/orders?role=landlord role=custom
@api.route('/orders', methods=['GET'])
@login_required
def get_orders():
    user_id = g.user_id
    role = request.args.get('role', '')

    try:
        if role == 'landlord':
            houses = House.query.filter(House.user_id==user_id).all()
            house_ids = [house.id for house in houses]
            orders = Order.query.filter(Order.house_id.in_(house_ids)).all()
        else:
            orders = Order.query.filter_by(user_id=user_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'查询订单错误')

    orders_li = []
    if orders:
        for order in orders:
            orders_li.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg=u'查询成功', data=orders_li)


@api.route('/order/<int:order_id>/status', methods=['PUT'])
@login_required
def accept_reject_order(order_id):
    # 获取参数
    user_id = g.user_id
    req_dict = request.get_json()
    if not req_dict:
        return jsonify(errno=RET.PARAMERR, errmsg=u'无效参数')

    action = req_dict.get('action')

    # 参数校验
    if action not in ('accept', 'reject'):
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数错误')

    try:
        order = Order.query.filter(Order.id==order_id, Order.status=='WAIT_ACCEPT').first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'查询订单错误')

    if house.user_id != user_id:
        return jsonify(errno=RET.ROLEERR, errmsg=u'不允许修改他人的订单')

    # 业务处理: 根据需要更改订单状态/添加说明
    if action == 'accept':
        order.status = 'WAIT_PAYMENT'
    else:
        order.status = 'REJECTED'
        reason = req_dict.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg=u'拒单原因缺失')
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'订单修改失败')

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'订单修改成功!')


@api.route('/order/<int:order_id>/comment', methods=['PUT'])
@login_required
def update_comment(order_id):
    # 接收数据
    user_id = g.user_id
    req_dict = request.get_json()
    comment = req_dict.get('comment')

    # 数据校验
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg=u'参数错误')

    try:
        order = Order.query.filter(Order.id==order_id, Order.user_id==user_id,
                                   Order.status=='WAIT_COMMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'查询订单错误')

    if not order:
        return jsonify(errno=RET.NODATA, errmsg=u'订单不存在')

    if user_id != order.user_id:
        return jsonify(errno=RET.ROLEERR, errsmg=u'不能评价他人订单')

    # 业务处理: 修改评论
    order.comment = comment
    order.status = 'COMPLETE'
    order.house.order_count += 1

    try:
        db.session.add(order)
        db.session.add(order.house)
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=u'添加评论失败')

    # 删除缓存数据
    try:
        redis_store.delete('house_info_%s' % order.house.id)
    except Exception as e:
        current_app.logger.error(e)

    # 返回响应
    return jsonify(errno=RET.OK, errmsg=u'评论添加成功')