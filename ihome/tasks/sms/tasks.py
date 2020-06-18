# -*-coding:utf-8-*-

from ihome.tasks.main import celery_app
from ihome.libs.yuntongxun.sms import CCP


@celery_app.task
def send_sms(to, datas, temp_id):
    ccp = CCP()
    return ccp.send_temp_sms(to, datas, temp_id)