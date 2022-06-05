import urllib.parse

from sanic_openapi import doc
from sanic.response import json
from common.dao.member import TtmMember
from common.helper.validator_helper import validate_params, IntegerField, CharField, ListField
from common.exceptions import ApiError,ApiCode
from common.libs.tokenize_util import encrypt_web_token,decrypt_web_token
from common.libs.aio import run_sqlalchemy
from common.libs.comm import now, total_number, to_strtime
from apps import mako, render_template
from typing import Dict, List, Tuple, Union
from sqlalchemy import and_, or_
import bcrypt
import datetime
import re
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
        'token': token,
        'msg':'操作成功'
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


@doc.summary('退出登录')
@doc.produces({
    'code': doc.Integer('状态码'),
    'data': {'status': doc.Boolean}
}, content_type='application/json', description='Request True')
async def logout(request):
    response = json({
        'code': ApiCode.SUCCESS,
        'data': {'status': 'True'}
    })
    response.cookies['token'] = ''
    response.cookies['token']['path'] = '/'
    response.cookies['token']['max-age'] = 0
    response.cookies['token']['domain'] = '.ttm.com'
    return response


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
        'avatar':ttm_member.avatar,
        'email': ttm_member.email,
        'phone': ttm_member.phone,
        'credit': ttm_member.credit,
        'level': ttm_member.level,
    }

    item = {
        'code': ApiCode.SUCCESS,
        'data': data,
        'msg': ''
    }
    return json(item)


@doc.summary('修改账号信息')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg': doc.String('消息提示'),
    'data': doc.Dictionary()
}, content_type='application/json', description='Request True')
@validate_params(
    CharField(name='name', required=False, allow_empty=False),
    IntegerField(name='phone', required=False),
    CharField(name='email', required=False, allow_empty=False),
    CharField(name='avatar', required=False, allow_empty=False),
)
@authorized()
async def up_detail(request,uid):
    name = request.json.get('name')
    phone = request.json.get('phone')
    email = request.json.get('email')
    avatar = request.json.get('avatar')
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    # token = request.cookies.get('Ttm-Token')
    # if not token:
    #     raise ApiError()
    # token = urllib.parse.unquote(token)
    # user_info = decrypt_web_token(token)
    # uid = user_info.get('uid')

    member = ttm_sql.query(TtmMember).filter(TtmMember.id == uid).first()
    print(member.name)
    if member:
        if name:
            member.name = name
        if email:
            member.email = email
        if avatar:
            member.avatar = avatar
        if phone:
            member.phone = phone
        ttm_sql.commit()
    return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})


@doc.summary('修改账号信息')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg': doc.String('消息提示'),
    'data': doc.Dictionary()
}, content_type='application/json', description='Request True')
@validate_params(
    CharField(name='password'),
    CharField(name='confirm_password'),
)
@authorized()
async def up_passwd(request, uid):
    password = request.valid_data.get('password')
    confirm_password = request.valid_data.get('confirm_password')
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    if password != confirm_password:
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='新密码与确认密码不一致')
    member = ttm_sql.query(TtmMember).filter(TtmMember.id == uid).first()
    if not bcrypt.checkpw(password.encode(), member.password.encode()):
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='原密码错误')
    member.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10))
    ttm_sql.commit()
    return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})


@doc.summary('用户信息')
# @route_acl('user_user_info', acl_required=False)
async def getInfo(request):
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    # print(request.args.get('0'))
    # print(request.cookies)
    # print(request.headers.get('cookie'))
    # token=request.headers['cookie']
    token = request.cookies.get('Ttm-Token')
    # print(token)

    if not token:
        raise ApiError()
    token= urllib.parse.unquote(token)
    user_info = decrypt_web_token(token)
    # print('__________', user_info)
    # print(user_info.get('uid'))
    uid = user_info.get('uid')

    @run_sqlalchemy()
    def get_user_data(db_session):
        return db_session.query(TtmMember).filter(TtmMember.id == uid).first()

    user = await get_user_data(ttm_sql)
    if not user:
        raise ApiError(code=200, msg='用户不存在')

    data = {
        'uid'       : user.id,
        'name'     : user.name,
        'avatar': f'http://cdn.qxiaolu.club/{user.avatar}' if user.avatar else f'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        'email': user.email,
        'phone': user.phone,
        'level': user.level,
        'money_nwdbl': str(user.money_nwdbl + user.money_wdbl),
        'created_at': to_strtime(user.created_at),
        'sex':'1'
    }
    return json({'code': ApiCode.SUCCESS, 'data': data})