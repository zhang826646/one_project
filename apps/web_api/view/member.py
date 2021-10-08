
from sanic_openapi import doc
from sanic.response import json
from common.dao.member import  Member


@doc.summary('登录')
# @doc.consumes(
#     doc.JsonBody({
#         'username': doc.String('用户名'),
#         'password': doc.String('密码'),
#     }), content_type='application/json', location='body', required=True
# )
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def login(request):
    son=request.app.min.get_mysql('min_sql')
    user=son.query(Member).filter(Member.id == 100000).first()
    item={
        'name':user.name,
        'phone':user.phone,
        'email':user.email
    }
    return json(item)
    # user_name=request.


async def info(request):
    son=request.app.min.get_mysql('min_sql')
    user=son.query(Member).filter(Member.id == 100000).first()
    item={
        'name':user.name,
        'phone':user.phone,
        'email':user.email
    }
    return json(item)