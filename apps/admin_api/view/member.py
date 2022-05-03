import copy
import re

import bcrypt
import re
from sanic.response import json
from sanic.exceptions import InvalidUsage
from sanic_openapi import doc
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import IntegrityError

from common.exceptions import ApiError, ApiCode
from common.dao.member import TtmMember
from common.libs.tokenize_util import encrypt_admin_token,decrypt_admin_token
from common.libs.comm import to_int, to_str, now, total_number, get_ipaddr
from common.libs.aio import run_sqlalchemy
from common.helper.validator_helper import validate_params, IntegerField, CharField, ListField



@doc.summary('用户列表')
async def member_list(request):
    page = request.json.get('pageNum', 1)
    limit = request.json.get('pageSize', 15)
    banned = request.json.get('banned')
    userName = request.json.get('userName')
    phonenumber = request.json.get('phonenumber')
    status = request.json.get('status')
    offset = (page - 1) * limit
    lists = []

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    # 条件筛选
    search_cond = True
    if userName:
        search_cond = TtmMember.name.like(f'%{userName}%')
    elif phonenumber:
            search_cond = TtmMember.phone == phonenumber


    # 封禁状态筛选
    if status:  # 只看正常账号
        search_cond = and_(search_cond, TtmMember.banned == status)

    orderby_cond = TtmMember.id.desc()

    @run_sqlalchemy()
    def get_member_list_data(db_session):
        return db_session.query(TtmMember) \
            .filter(search_cond) \
            .order_by(orderby_cond) \
            .offset(offset).limit(limit) \
            .all()

    rows = await get_member_list_data(ttm_sql)


    for row in rows:
        lists.append({
            'userId'              : row.id,
            'userName'             : row.name,
            'nickName': row.name,
            'avatar'           : r'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'level'            : row.level,
            'phonenumber'            : row.phone if row.phone else '',
            'status'           : str(row.banned),
            'vip'              : row.vip_expire_at > now(),
            'money_nwdbl'      : row.money_nwdbl,
            'money_wdbl'       : row.money_wdbl,
            'created_at'       : row.created_at,

        })
    total = await total_number(ttm_sql,TtmMember.id ,search_cond)
    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'total'       : total,
        'data'        : lists,
    }
    print(data)
    return json(data)

@doc.summary('用户列表')
async def detail(request,id):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    # 条件筛选
    search_cond = TtmMember.id == id

    search_cond = and_(search_cond, TtmMember.banned == 0)



    @run_sqlalchemy()
    def get_member_list_data(db_session):
        return db_session.query(TtmMember) \
            .filter(search_cond) \
            .first()

    row = await get_member_list_data(ttm_sql)

    lists={
        'userId'              : row.id,
        'userName'             : row.name,
        'nickName': row.name,
        'avatar'           : r'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        'level'            : row.level,
        'phonenumber'            : row.phone if row.phone else '',
        'status'           : row.banned,
        'email':row.email,
        'sex': row.sex,
        'remark': row.remark,
        'vip'              : row.vip_expire_at > now(),
        'money_nwdbl'      : row.money_nwdbl,
        'money_wdbl'       : row.money_wdbl,
        'created_at'       : row.created_at,

    }

    data = {
        'code'        : ApiCode.SUCCESS,
        'data'        : lists,
    }
    print(data)
    return json(data)



@doc.summary('添加新用户')
async def add_member(request):
    uid = request.json.get('userId')
    name = request.json.get('userName')
    avatar = request.json.get('avatar')
    zone = request.json.get('zone') or '86'
    phone = request.json.get('phonenumber')
    password = request.json.get('password')
    email = request.json.get('email')
    sex = request.json.get('sex',1)
    remark = request.json.get('remark')

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')


    if uid:
        item =ttm_sql.query(TtmMember).filter(TtmMember.id == uid).first()
    else:
        member = ttm_sql.query(TtmMember).filter(or_(TtmMember.name == name,
                                                     TtmMember.phone == phone)).first()
        if member:
            raise ApiError(code=ApiCode.NORMAL_ERR, msg='昵称或手机号已存在')
        item = TtmMember()
        ttm_sql.add(item)
    item.name = name
    # item.avatar = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'
    item.avatar = ''
    item.zone = zone
    item.phone = phone
    item.email = email
    item.sex = sex
    item.remark = remark
    item.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    item.created_at = item.updated_at = now()
    ttm_sql.commit()

    return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})


@doc.summary('修改用户状态')
async def statu_member(request):
    uid = request.json.get('userId')
    status = request.json.get('status',1)

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    if uid:
        item =ttm_sql.query(TtmMember).filter(TtmMember.id == uid).first()
        if not item:
            raise ApiError(code=ApiCode.NORMAL_ERR, msg='用户不存在')
    item.banned = status
    ttm_sql.commit()

    return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})


@doc.summary('更新密码')
@doc.consumes(
    doc.JsonBody({
        'password'        : doc.String('原密码'),
        'new_password'    : doc.String('新密码'),
        'confirm_password': doc.String('确认密码')
    }), content_type='application/json', location='body', required=True
)
async def update_password(request):
    uid = request.json.get('userId')

    password = request.json.get('password')

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')


    user = ttm_sql.query(TtmMember).filter(TtmMember.id == uid).first()
    # if not bcrypt.checkpw(password.encode(), user.password.encode()):
    #     raise ApiError(code=ApiCode.NORMAL_ERR, msg='原密码错误')
    user.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10))
    ttm_sql.commit()
    return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})