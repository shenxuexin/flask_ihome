#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8aaf07087291adde0172acbefc020f22'

#���ʺ�Token
accountToken= 'a1005976685449889b7f0e2a5369eb44'

#Ӧ��Id
appId='8aaf07087291adde0172acbefd0c0f29'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id


class CCP(object):
    '''��װ�����Ʒ��Ͷ��Žӿ�: ����ģʽ'''
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            obj = super(CCP, cls).__new__(cls)

            # ��ʼ��REST SDK
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


# sendTemplateSMS(�ֻ�����,��������,ģ��Id)
if __name__ == '__main__':
    ccp = CCP()
    ret = ccp.send_temp_sms('13161120588', ['1234', 5], 1)
    print(ret)