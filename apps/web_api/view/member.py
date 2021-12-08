from sanic_openapi import doc
from sanic.response import json
from common.dao.member import TtmMember
from common.helper.validator_helper import validate_params, IntegerField, CharField, ListField
from common.exceptions import ApiError,ApiCode
from common.libs.tokenize_util import encrypt_app_token
from common.libs.aio import run_sqlalchemy
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
@mako.template('base.html')
async def index(request):
    # print(mako)

    # data={'data':{[
    #     {'url': 'https://www.baidu.com','created_at': 1635921870,'tags': [{'url':'123','name':'zhang'},{'url':'234','name':'min'}],'excerpt':'excerpt' },
    #     {'url': 'https://www.baidu.com', 'created_at': 1635955555,'tags': [{'url': '123', 'name': 'zhangzhang'}, {'url': '234', 'name': 'minmin'}], 'excerpt': 'excerpt2'},
    # ]}}
    # return jinja.render("index.html", request, item)
    # print('json+++++',data)
    # return { ['Hello, sanic!',123,'123']}
    new_time=datetime.datetime.fromtimestamp(1636366351)
    data={'data':[{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]},{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]}]}
    # data={'users':[{'name':'user1'},{'name':'user2'},{'name':'user3'},{'name':'user4'},{'name':'user5'},{'name':'user6'}]}
    return data
    # return json(data)



@doc.summary('登录')
@doc.consumes(
    doc.JsonBody({
        'username': doc.String('用户名'),
        'password': doc.String('密码'),
    }), content_type='application/json', location='body', required=True
)
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
@validate_params(
    CharField(name='username', allow_empty=False),
    CharField(name='password', allow_empty=False),
)
async def login(request):
    username = request.valid_data.get('username')
    password = request.valid_data.get('password')
    ttm_sql = request.app.leisu.get_mysql('ttm_sql')

    cond = TtmMember.banned == 0  # banned 1禁用 0正常
    ttm_member = ttm_sql.query(TtmMember).filter(TtmMember.name == username, cond).first()
    ttm_member = ttm_member or ttm_sql.query(TtmMember).filter(TtmMember.email == username, cond).first()

    if not ttm_member:
        raise ApiError(code=ApiCode.PARAM_ERR, msg='用户不存在')
    if not bcrypt.checkpw(password.encode(), ttm_member.password.encode()):
        raise ApiError(code=ApiCode.PARAM_ERR, msg='密码错误')



    token = encrypt_app_token({'uid': ttm_member.id, 'time': now()})
    response = json({
        'code': ApiCode.SUCCESS,
        'data': {'token': token}
    })
    response.cookies['token'] = token
    response.cookies["token"]['path'] = '/'
    response.cookies['token']['max-age'] = 86400 * 7
    response.cookies['token']['domain'] = ''
    response.cookies['token']['httponly'] = True
    response.cookies['token']['secure'] = True
    response.cookies['token']['samesite'] = None

    return response



async def info(request):
    son=request.app.min.get_mysql('min_sql')
    user=son.query(TtmMember).filter(TtmMember.id == 100000).first()
    item={
        'name':user.name,
        'phone':user.phone,
        'email':user.email
    }
    return json(item)