# -*-coding:utf-8-*-

from celery import Celery
from ihome.libs.yuntongxun.sms import CCP

# 创建celery对象
celery_app = Celery('ihome', broker='redis://192.168.153.131:6379/1')


@celery_app.task
def send_sms(to, datas, temp_id):
    ccp = CCP()
    ccp.send_temp_sms(to, datas, temp_id)