# -*- coding: utf-8 -*-

from qiniu import Auth, put_data, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'KVqBo0dgmz8u37cWjo5ICJoD05nojNC5iJ3n8yjt'
secret_key = 'qiXQVReLSEkRO8tdiQIwBkf4sHeaCajJ0xy0h_Tr'


def storage(data):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome-shen'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    # 要上传文件的本地路径
    ret, info = put_data(token, None, data)
    print(ret)

    if info.status_code == 200:
        return ret.get('key')
    else:
        raise Exception(u'文件上传失败')


if __name__ == '__main__':
    with open('home01.jpg', 'rb') as f:
        storage(f.read())
