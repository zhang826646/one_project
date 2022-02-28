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
@validate_params(
    IntegerField(name='page', required=False, min_value=1),
    IntegerField(name='limit', required=False, min_value=1),
    IntegerField(name='banned', required=False, nullable=True),
    IntegerField(name='search_type', required=False, nullable=True),
    CharField(name='search_field', required=False, allow_empty=True),
    CharField(name='search_keyword', required=False, allow_empty=True),
)
async def member_list(request):
    page = request.valid_data.get('page', 1)
    limit = request.valid_data.get('limit', 15)
    banned = request.valid_data.get('banned')
    search_type = request.valid_data.get('search_type')
    search_field = request.valid_data.get('search_field')
    search_keyword = request.valid_data.get('search_keyword')
    offset = (page - 1) * limit
    lists = []

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    # 条件筛选
    search_cond = True
    if search_field and search_keyword:
        if search_field == 'uid':
            search_cond = TtmMember.id == to_int(search_keyword)

        elif search_field == 'name':
            if search_type == 0:  # 精确查找
                search_cond = TtmMember.name == search_keyword
            else:  # 模糊查找
                search_cond = TtmMember.name.like(f'%{search_keyword}%')
        elif search_field == 'phone':
            if search_type == 0:
                search_cond = TtmMember.phone == search_keyword
            else:
                search_cond = TtmMember.phone.like(f'%{search_keyword}%')

    # 封禁状态筛选
    if banned == 0:  # 只看正常账号
        search_cond = and_(search_cond, TtmMember.banned == 0)
    elif banned == 1:  # 只看封禁账号
        search_cond = and_(search_cond, TtmMember.banned == 1)


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
            'uid'              : row.id,
            'name'             : row.name,
            'avatar'           : r'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'level'            : row.level,
            'phone'            : '***********' if row.phone else '',
            'banned'           : row.banned,
            'vip'              : row.vip_expire_at > now(),
            'money_nwdbl'      : row.money_nwdbl,
            'money_wdbl'       : row.money_wdbl,
            'created_at'       : row.created_at,

        })

    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'total'       : 10,
        'data'        : lists,
    }
    return json(data)


@doc.summary('添加新用户')
@validate_params(
    CharField(name='name'),
    CharField(name='avatar', required=False, allow_empty=True),
    CharField(name='zone', required=False, allow_empty=True),
    CharField(name='phone'),
    CharField(name='password'),
    CharField(name='email', required=False)
)
async def add_member(request):
    name = request.valid_data.get('name')
    avatar = request.valid_data.get('avatar')
    zone = request.valid_data.get('zone') or '86'
    phone = request.valid_data.get('phone')
    password = request.valid_data.get('password')
    email = request.valid_data.get('email')
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    member = ttm_sql.query(TtmMember).filter(or_(TtmMember.name == name,
                                                 TtmMember.phone == phone)).first()
    if member:
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='用户已存在')

    item = TtmMember()
    item.name = name
    item.avatar = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'
    item.zone = zone
    item.phone = phone
    item.email = email
    item.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    item.created_at = item.updated_at = now()
    ttm_sql.add(item)
    ttm_sql.commit()

    return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})