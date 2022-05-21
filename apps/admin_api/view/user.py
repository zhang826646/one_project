import bcrypt
import re
from sanic.response import json
from sanic.exceptions import InvalidUsage
from sanic_openapi import doc
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError

from common.exceptions import ApiError, ApiCode
from common.dao.user import User
from common.libs.tokenize_util import encrypt_admin_token,decrypt_admin_token
from common.libs.comm import to_int, to_str, now, total_number, get_ipaddr
from common.libs.aio import run_sqlalchemy
from common.helper.validator_helper import validate_params, IntegerField, CharField, ListField


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

    cond = and_(User.status == 1, User.banned == 0)  # banned 1禁用 0正常
    user = ttm_sql.query(User).filter(User.name == username, cond).first()
    user = user or ttm_sql.query(User).filter(User.email == username, cond).first()

    if not user:
        raise ApiError(code=ApiCode.PARAM_ERR, msg='用户不存在')
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise ApiError(code=ApiCode.PARAM_ERR, msg='密码错误')

    user.last_login = now()
    ttm_sql.commit()

    token = encrypt_admin_token({'uid': user.id, 'user_name': user.name,
                                 'user_real_name': user.real_name, 'time': now()})
    response = json({
        'code': ApiCode.SUCCESS,
        'token': token,
        'msg':'操作成功'
    })
    response.cookies['token'] = token
    response.cookies["token"]['path'] = '/'
    response.cookies['token']['max-age'] = 86400 * 7
    response.cookies['token']['domain'] = '.ttm.com'
    response.cookies['token']['httponly'] = True
    response.cookies['token']['secure'] = True
    response.cookies['token']['samesite'] = None

    return response


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


@doc.summary('用户信息（含权限组列表信息）')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {
        'id'       : doc.Integer('用户 ID'),
        'name'     : doc.String('用户名'),
        'real_name': doc.String('姓名'),
        'role'     : {
            'id'             : doc.Integer('用户组 ID'),
            'name'           : doc.String('用户组 键名'),
            'description'    : doc.String('用户组 描述'),
            'active'         : doc.String('激活 [0:暂停|1:正常]'),
            'permission_list': doc.List(doc.String('权限'))
        }
    }
}, content_type='application/json', description='Request True')
# @route_acl('user_user_info', acl_required=False)
async def info(request):
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    token=request.headers['access-token']
    # token = request.args['Access-Token'][0]

    user_info = decrypt_admin_token(token)
    print('__________', user_info)
    uid = user_info.get('uid')

    @run_sqlalchemy()
    def get_user_data(db_session):
        return db_session.query(User).filter(User.id == uid).first()

    user = await get_user_data(ttm_sql)
    if not user or user.status == 0:
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='用户不存在')

    roles = ['admin']
    data = {
        # 'id'       : user.id,
        'name'     : user.name,
        'avatar': f'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        'introduction': "I am a super administrator",
        'roles'    : roles
    }
    return json({'code': ApiCode.SUCCESS, 'data': data})


@doc.summary('用户信息（含权限组列表信息）')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {
        'id'       : doc.Integer('用户 ID'),
        'name'     : doc.String('用户名'),
        'real_name': doc.String('姓名'),
        'role'     : {
            'id'             : doc.Integer('用户组 ID'),
            'name'           : doc.String('用户组 键名'),
            'description'    : doc.String('用户组 描述'),
            'active'         : doc.String('激活 [0:暂停|1:正常]'),
            'permission_list': doc.List(doc.String('权限'))
        }
    }
}, content_type='application/json', description='Request True')
# @route_acl('user_user_info', acl_required=False)
async def getInfo(request):
    return json({"msg": "操作成功", "code": 200, "permissions": ["*:*:*"], "roles": ["admin"],
                 "user": {"searchValue": None, "createBy": "admin", "createTime": "2021-09-09 17:25:28",
                          "updateBy": None, "updateTime": None, "remark": "管理员", "params": {}, "userId": 1,
                          "deptId": 103, "userName": "admin", "nickName": "若依", "email": "ry@163.com",
                          "phonenumber": "15888888888", "sex": "1", "avatar": "", "status": "0", "delFlag": "0",
                          "loginIp": "61.134.209.47", "loginDate": "2022-03-20T18:07:21.000+08:00",
                          "dept": {"searchValue": None, "createBy": None, "createTime": None, "updateBy": None,
                                   "updateTime": None, "remark": None, "params": {}, "deptId": 103, "parentId": 101,
                                   "ancestors": None, "deptName": "研发部门", "orderNum": "1", "leader": "若依",
                                   "phone": None, "email": None, "status": "0", "delFlag": None, "parentName": None,
                                   "children": []}, "roles": [
                         {"searchValue": None, "createBy": None, "createTime": None, "updateBy": None,
                          "updateTime": None, "remark": None, "params": {}, "roleId": 1, "roleName": "超级管理员",
                          "roleKey": "admin", "roleSort": "1", "dataScope": "1", "menuCheckStrictly": False,
                          "deptCheckStrictly": False, "status": "0", "delFlag": None, "flag": False, "menuIds": None,
                          "deptIds": None, "admin": True}], "roleIds": None, "postIds": None, "roleId": None,
                          "admin": True}})



# @doc.summary('账号信息（用于修改账号信息时的展示）')
# @doc.produces({
#     'code': doc.Integer('状态码'),
#     'msg' : doc.String('消息提示'),
#     'data': {
#         'id'       : doc.Integer('账号 ID'),
#         'real_name': doc.String('姓名'),
#         'email'    : doc.String('邮箱')
#     }
# }, content_type='application/json', description='Request True')
# @route_acl(route_name='user_get_detail', acl_required=False)
# async def get_detail(request):
#     user_id = request['user_id']
#     leisu_www = request.app.leisu.get_mysql('leisu_www')
#
#     user = leisu_www.query(User).filter(User.id == user_id).first()
#     data = {
#         'id'       : user.id,
#         'real_name': user.real_name,
#         'email'    : user.email,
#     }
#     return json({'code': ApiCode.SUCCESS, 'data': data})
#
#
# @doc.summary('更新邮箱')
# @doc.consumes(
#     doc.JsonBody({
#         'email': doc.String('邮箱')
#     }), content_type='application/json', location='body', required=True
# )
# @doc.produces({
#     'code': doc.Integer('状态码'),
#     'msg' : doc.String('消息提示'),
# }, content_type='application/json', description='Request True')
# @route_acl('user_update_email')
# @logged(op='更新邮箱')
# @validate_params(
#     CharField(name='email', allow_empty=False)
# )
# async def update_email(request):
#     user_id = request['user_id']
#     email = request.valid_data.get('email')
#
#     if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
#         raise ApiError(code=ApiCode.PARAM_ERR, msg='邮箱格式不正确')
#
#     leisu_www = request.app.leisu.get_mysql('leisu_www')
#
#     user = leisu_www.query(User).filter(User.id == user_id).first()
#     user.email = email
#     leisu_www.commit()
#     return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})
#
#
# @doc.summary('更新密码')
# @doc.consumes(
#     doc.JsonBody({
#         'password'        : doc.String('原密码'),
#         'new_password'    : doc.String('新密码'),
#         'confirm_password': doc.String('确认密码')
#     }), content_type='application/json', location='body', required=True
# )
# @doc.produces({
#     'code': doc.Integer('状态码'),
#     'msg' : doc.String('消息提示'),
# }, content_type='application/json', description='Request True')
# @route_acl('user_update_password', acl_required=False)
# @logged(op='更新密码', field_regex='.*')
# @validate_params(
#     CharField(name='password', allow_empty=False),
#     CharField(name='new_password'),
#     CharField(name='confirm_password')
# )
# async def update_password(request):
#     password = request.valid_data.get('password')
#     new_password = request.valid_data.get('new_password')
#     confirm_password = request.valid_data.get('confirm_password')
#
#     if new_password != confirm_password:
#         raise ApiError(code=ApiCode.NORMAL_ERR, msg='新密码与确认密码不一致')
#
#     leisu_www = request.app.leisu.get_mysql('leisu_www')
#
#     user_id = request['user_id']
#
#     user = leisu_www.query(User).filter(User.id == user_id).first()
#     if not bcrypt.checkpw(password.encode(), user.password.encode()):
#         raise ApiError(code=ApiCode.NORMAL_ERR, msg='原密码错误')
#     user.password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(10))
#     leisu_www.commit()
#     return json({'code': ApiCode.SUCCESS, 'msg': '保存成功'})
#
#


#
# @doc.summary('后台账户列表')
# @doc.consumes(
#     doc.JsonBody({
#         'page'          : doc.Integer('页码'),
#         'limit'         : doc.Integer('每页条数'),
#         'banned'        : doc.Integer('禁用 [0:否|1:是]'),
#         'order_by_field': doc.String('排序 last_login_asc:登录时间正序 last_login_desc:登录时间倒序'),
#         'search_field'  : doc.String('name:用户名 real_name:真实姓名 group_id:用户组'),
#         'search_keyword': doc.String(),
#     }), content_type='application/json', location='body', required=True
# )
# @doc.produces({
#     'code'        : doc.Integer('状态码'),
#     'msg'         : doc.String('消息提示'),
#     'current_page': doc.Integer('当前页码'),
#     'page_size'   : doc.Integer('每页条数'),
#     'total'       : doc.Integer('总共条数'),
#     'data'        : doc.List({
#         'id'        : doc.Integer('用户 ID'),
#         'name'      : doc.String('用户名'),
#         'real_name' : doc.String('姓名'),
#         'email'     : doc.String('邮箱'),
#         'status'    : doc.Integer('状态 [1:正常|0:不存在]'),
#         'banned'    : doc.Integer('禁用 [0:否|1:是]'),
#         'group_id'  : doc.Integer('用户组 ID'),
#         'group_name': doc.String('用户组 描述'),
#         'last_login': doc.Integer('上次登录时间'),
#         'created_at': doc.Integer('创建时间'),
#         'updated_at': doc.Integer('更新时间')
#     }),
# }, content_type='application/json', description='Request True')
# @route_acl('user_user_list')
# @validate_params(
#     IntegerField(name='page', min_value=1, required=False),
#     IntegerField(name='limit', min_value=1, required=False),
#     IntegerField(name='banned', min_value=0, max_value=1, required=False),
#     CharField(name='order_by_field', required=False),
#     CharField(name='search_field', required=False, allow_empty=True),
#     CharField(name='search_keyword', required=False, allow_empty=True)
# )
# async def user_list(request):
#     page = request.valid_data.get('page', 1)
#     limit = request.valid_data.get('limit', 50)
#     banned = request.valid_data.get('banned')
#     order_by_field = request.valid_data.get('order_by_field', '')
#     search_field = request.valid_data.get('search_field')
#     search_keyword = request.valid_data.get('search_keyword')
#
#     offset = (page - 1) * limit
#     lists = []
#
#     cond = User.status == 1
#     if banned in (0, 1):
#         cond = and_(cond, User.banned == banned)
#     if search_field and search_keyword:
#         if search_field == 'name':
#             cond = and_(cond, User.name.like(f'%%{search_keyword}%%') )
#         elif search_field == 'real_name':
#             cond = and_(cond, User.real_name.like(f'%%{search_keyword}%%'))
#         elif search_field == 'group_id':
#             cond = and_(cond, User.group_id == to_int(search_keyword))
#
#     if order_by_field == 'last_login_asc':
#         order_by = User.last_login.asc()
#     elif order_by_field == 'last_login_desc':
#         order_by = User.last_login.desc()
#     else:
#         order_by = User.created_at.desc()
#
#     leisu_www = request.app.leisu.get_mysql('leisu_www')
#
#     @run_sqlalchemy()
#     def get_user_list_data(db_session):
#         return db_session.query(User, UserGroup)\
#             .join(UserGroup, UserGroup.id == User.group_id) \
#             .filter(cond) \
#             .order_by(order_by) \
#             .offset(offset) \
#             .limit(limit).all()
#
#     rows = await get_user_list_data(leisu_www)
#     total = await total_number(leisu_www, User.id, cond)
#
#     for row in rows:
#         lists.append({
#             'id'        : row.User.id,
#             'name'      : row.User.name,
#             'real_name' : row.User.real_name,
#             'email'     : row.User.email,
#             'status'    : row.User.status,
#             'banned'    : row.User.banned,
#             'group_id'  : row.User.group_id,
#             'group_name': row.UserGroup.description,
#             'last_login': row.User.last_login,
#             'created_at': row.User.created_at.timestamp() if row.User.created_at else 0,
#             'updated_at': row.User.updated_at.timestamp() if row.User.updated_at else 0
#         })
#
#     data = {
#         'code'        : ApiCode.SUCCESS,
#         'current_page': page,
#         'page_size'   : limit,
#         'total'       : total,
#         'data'        : lists
#     }
#     return json(data)