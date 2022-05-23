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
