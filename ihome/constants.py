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

# 地区信息缓存的存储时间, 单位:秒
AREA_INFO_REDIS_CACHE_EXPIRE = 7200

# 首页查询的房屋数目
HOME_SHOW_HOUSES_NUM = 5

# 首页查询的房屋信息缓存时间, 单位:秒
HOME_HOUSES_REDIS_EXPIRE = 7200

# 房屋详情展示的最大评论数
HOUSE_INFO_COMMENTS_MAX_NUM = 30

# 房屋详情信息缓存信息保存时间, 单位: 秒
HOUSE_INFO_REDIS_EXPIRE = 7200

# 每一页展示的数据量
PER_PAGE_CAPACITY = 2

# 房屋列表页的缓存保存时间
HOUSE_LIST_REDIS_CACHE_EXPIRE = 7200

# 支付宝支付页面地址
ALIPAY_PATH_PREFIX = 'https://openapi.alipaydev.com/gateway.do?'

