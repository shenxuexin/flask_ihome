# -*-coding:utf-8-*-

# 图片验证码过期时间, 单位:秒
IMAGE_CODE_REDIS_EXPIRE = 180

# 手机验证码过期事件, 单位:秒
SMS_CODE_REDIS_EXPIRE = 300

# 手机验证码获取时间间隔, 单位:秒
SEND_SMS_CODE_INTERVAL = 60

# 同一个ip尝试错误的最大次数
LOGIN_TRY_WRONG_NUM = 5

# 用户尝试登录记录的保存时间
LOGIN_TRY_RECORD_MAX_TIME = 600

# 七牛的链接域名
QINIU_URL_DOMIN = 'http://qc1s4rf9r.bkt.clouddn.com/'
