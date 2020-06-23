# flask_ihome

## 项目简介
项目名称：爱家租房    
项目描述：手机网站, 移动端租房项目(前后端分离)    
技术应用：flask, celery, jquery, html5等        
主要功能：   
用户模块: 用户注册(验证码, 手机号码验证等), 用户登录, 登出, 个人中心    
房屋模块：首页, 房屋搜索(区域,日期筛选与排序), 房屋详情, 发布房源    
订单模块：订单提交, 接单拒单, 订单支付, 订单评论    

## 目录结构说明
1. manage.py: 启动文件    
2. config.py: 配置文件
3. ihome.sql: 测试数据库
4. migrations: 数据库迁移相关文件目录
5. logs: 日志文件目录
6. requirement.txt: python依赖模块文件   
7. ihome: 主要业务目录
    1. api_v_1_0: 功能模块目录
    2. libs: 第三方工具目录
    3. static: 静态文件目录(html, css, js, images)
    4. tasks: celery任务目录
    5. util: 自定义工具目录
    6. constance.py: 相关常量定义文件
    7. models: 数据库模型类
    8. response_code.py: 状态响应码
    9. web_html.py: 静态页面蓝图

## 静态页面
html    
├── auth.html: 实名认证页面    
├── booking.html: 房屋预订页面     
├── detail.html: 房屋详情页面    
├── index.html: 首页    
├── login.html: 登录页面    
├── lorders.html: 客户订单页面    
├── myhouse.html: 个人房源页面    
├── my.html: 个人中心页面   
├── newhouse.html: 发布房源页面   
├── orders.html: 个人订单页面   
├── pay_complete.html: 支付结果返回页面   
├── profile.html: 个人信息修改页面   
├── register.html: 注册页面    
└── search.html: 搜索页面   

