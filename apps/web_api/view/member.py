from sanic_openapi import doc
# from sanic.response import json
from common.dao.member import  Member
from apps import mako,render_template
from typing import Dict, List, Tuple, Union
# from apps import jinja
import datetime




@doc.summary('主页')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
@mako.template('index.html')
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



async def info(request):
    son=request.app.min.get_mysql('min_sql')
    user=son.query(Member).filter(Member.id == 100000).first()
    item={
        'name':user.name,
        'phone':user.phone,
        'email':user.email
    }
    return json(item)