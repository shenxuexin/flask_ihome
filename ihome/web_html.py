# -*-coding:utf-8-*-

from flask import Blueprint, current_app, make_response
from flask_wtf import csrf

html = Blueprint('web_html', __name__)


@html.route('/<re(r".*"):html_file_name>')
def get_html(html_file_name):
    print(current_app.url_map)
    if not html_file_name:
        html_file_name = 'index.html'

    if html_file_name != 'favicon.ico':
        html_file_name = 'html/' + html_file_name

    # 生成csrf_token值
    csrf_token = csrf.generate_csrf()

    # 设置cookie
    resp = make_response(current_app.send_static_file(html_file_name))
    resp.set_cookie('csrf_token', csrf_token)

    return resp