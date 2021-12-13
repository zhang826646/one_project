from sanic_openapi import doc
from sanic.response import json
from common.dao.member import TtmMember
from common.helper.validator_helper import validate_params, IntegerField, CharField, ListField
from common.exceptions import ApiError,ApiCode
from common.libs.tokenize_util import encrypt_web_token
from common.libs.aio import run_sqlalchemy
from common.libs.comm import now
from apps import mako,render_template
from typing import Dict, List, Tuple, Union
from sqlalchemy import and_,or_
import bcrypt
import datetime
from apps.web_api.decorators import authorized



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
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    cond = TtmMember.banned == 0  # banned 1禁用 0正常
    cond = and_(cond,or_(TtmMember.email == username,TtmMember.name == username,TtmMember.phone == username))

    @run_sqlalchemy()
    def get_menber(db_session):
        return db_session.query(TtmMember).filter(cond).first()
    ttm_member = await get_menber(ttm_sql)

    if not ttm_member:
        raise ApiError(code=ApiCode.PARAM_ERR, msg='用户不存在')
    if not bcrypt.checkpw(password.encode(), ttm_member.password.encode()):
        raise ApiError(code=ApiCode.PARAM_ERR, msg='密码错误')


    token = encrypt_web_token({'uid': ttm_member.id, 'time': now()})
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
    # return json(response)


@doc.summary('注册')
@doc.consumes(
    doc.JsonBody({
        'username': doc.String('用户名'),
        'password': doc.String('密码'),
        'confirm_password': doc.String('确认密码'),
        'phone'      : doc.Integer('手机号'),
        'code'       : doc.String('验证码'),
        'zone'       : doc.Integer('区号'),
        'email'         :doc.String('邮箱'),
    }), content_type='application/json', location='body', required=True
)
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
@validate_params(
    CharField(name='username'),
    CharField(name='password' ),
    CharField(name='confirm_password'),
    IntegerField(name='phone'),
    IntegerField(name='zone',required=False),
    CharField(name='code'),
    CharField(name='email',required=False, allow_empty=False),
)
async def register(request):
    username = request.valid_data.get('username')
    password = request.valid_data.get('password')
    confirm_password = request.valid_data.get('confirm_password')
    phone = request.valid_data.get('phone')
    zone = request.valid_data.get('zone', 86)
    code = request.valid_data.get('code')
    email = request.valid_data.get('email')
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    if password != confirm_password:
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='密码与确认密码不一致')
    if not code:
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='验证码错误')
    cond = or_(TtmMember.email == email, TtmMember.name == username, TtmMember.phone == phone)

    @run_sqlalchemy()
    def get_menber(db_session):
        return db_session.query(TtmMember).filter(cond).first()

    ttm_member = await get_menber(ttm_sql)
    if ttm_member:
        raise ApiError(code=ApiCode.PARAM_ERR, msg='用户信息已存在')
    member = TtmMember()
    member.name = username
    member.email = email
    member.zone = zone
    member.phone = phone
    member.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10))
    ttm_sql.add(member)
    ttm_sql.commit()

    item = {
        'code': ApiCode.SUCCESS,
        'msg': '注册成功'
    }
    return json(item)
    # return item


@doc.summary('账号信息')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg': doc.String('消息提示'),
    'data': doc.Dictionary()
}, content_type='application/json', description='Request True')
@authorized()
async def get_detail(request, uid):
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    @run_sqlalchemy()
    def get_menber(db_session):
        return db_session.query(TtmMember).filter(TtmMember.id == uid).first()

    ttm_member = await get_menber(ttm_sql)
    data = {
        'id': ttm_member.id,
        'name': ttm_member.name,
    }

    item = {
        'code': ApiCode.SUCCESS,
        'data': data,
        'msg': ''
    }
    return json(item)
