#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8aaf07087291adde0172acbefc020f22'

#主帐号Token
accountToken= 'a1005976685449889b7f0e2a5369eb44'

#应用Id
appId='8aaf07087291adde0172acbefd0c0f29'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id


class CCP(object):
    '''封装容联云发送短信接口: 单例模式'''
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)

            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj

        return cls.instance

    def send_temp_sms(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)

        # smsMessageSid:e3cb47cf1cad4f368d211679bb8960f6
        # dateCreated:20200613164254
        # statusCode:000000

        if result.get('statusCode') == '000000':
            return 0
        else:
            return -1


# sendTemplateSMS(手机号码,内容数据,模板Id)
if __name__ == '__main__':
    ccp = CCP()
    ret = ccp.send_temp_sms('13161120588', ['1234', 5], 1)
    print(ret)