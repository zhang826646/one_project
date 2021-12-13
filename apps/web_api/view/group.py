from sanic_openapi import doc
from sanic.response import json
from common.dao.member import TtmMember
from common.helper.validator_helper import validate_params, IntegerField, CharField, ListField
from common.exceptions import ApiError,ApiCode
from common.libs.tokenize_util import encrypt_app_token
from common.libs.aio import run_sqlalchemy
from common.libs.comm import now
from apps import mako,render_template
from typing import Dict, List, Tuple, Union
# from apps import jinja
from sqlalchemy import and_,or_
import bcrypt
import datetime



@doc.summary('主页')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
@mako.template('index.html')
async def index(request):

    new_time=datetime.datetime.fromtimestamp(1636366351)
    data={'data':[{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]},{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]}]}
    # data={'users':[{'name':'user1'},{'name':'user2'},{'name':'user3'},{'name':'user4'},{'name':'user5'},{'name':'user6'}]}
    return data
    # return json(data)