# -*-coding:utf-8-*-

from . import api
from ihome.util.commens import login_required
from flask import g, request, jsonify, current_app
from ihome.models import Order
from ihome.response_code import RET
from ihome import constants, db
from alipay import AliPay
import os


@api.route('/order/<int:order_id>/payment', methods=['POST'])
@login_required
def ali_order_pay(order_id):
    user_id = g.user_id
    try:
        order = Order.query.filter(Order.id==order_id, Order.user_id==user_id, Order.status=='WAIT_PAYMENT').first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'订单查询异常')

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg=u'无效的订单号')

    # 初始化
    app_private_key_path = os.path.join(os.path.dirname(__file__), 'keys/app_private_key.pem')
    alipay_public_key_path = os.path.join(os.path.dirname(__file__), 'keys/alipay_public_key.pem')

    try:
        alipay_client = AliPay(
            appid='2016092000556267',
            app_notify_url='http://127.0.0.1',  # 默认回调url
            app_private_key_path=app_private_key_path,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=alipay_public_key_path,
            sign_type='RSA2',  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        order_string = alipay_client.api_alipay_trade_wap_pay(
            out_trade_no=order.id,
            total_amount=str(order.amount/100.0),
            subject=u'爱家租房_%d' % order.id,
            return_url='http://127.0.0.1:5000/pay_complete.html',
            # app_notify_url=''  # 可选, 不填则使用默认notify url
        )
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg=u'第三方支付异常')

    pay_url = constants.ALIPAY_PATH_PREFIX+order_string

    return jsonify(errno=RET.OK, errmsg='OK', pay_url=pay_url)


@api.route('/order/payment', methods=['PUT'])
def verify_payment():
    data = request.form.to_dict()
    # sign 不能参与签名验证
    signature = data.pop('sign')

    app_private_key_path = os.path.join(os.path.dirname(__file__), 'keys/app_private_key.pem')
    alipay_public_key_path = os.path.join(os.path.dirname(__file__), 'keys/alipay_public_key.pem')

    alipay_client = AliPay(
        appid='2016092000556267',
        app_notify_url='http://127.0.0.1',  # 默认回调url
        app_private_key_path=app_private_key_path,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=alipay_public_key_path,
        sign_type='RSA2',  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    # verify
    success = alipay_client.verify(data, signature)
    if success:
        try:
            order_id = data.get('out_trade_no')
            trade_no = data.get('trade_no')
            Order.query.filter(Order.id==order_id).update({'status': 'WAIT_COMMENT', 'trade_no': trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()

    return jsonify(errno=RET.OK, errmsg='OK')