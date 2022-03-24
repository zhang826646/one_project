from sanic_openapi import doc
from sanic.response import json
from apps import mako,render_template
from typing import Dict, List, Tuple, Union
from sqlalchemy import and_,or_
import datetime
import re
import ujson
from common.dao.circle import CirclePost,CircleComment
from common.dao.member import TtmMember
from common.exceptions import ApiError,ApiCode
from common.libs.aio import run_sqlalchemy
from common.libs.comm import now
from apps import mako


@doc.summary('获取文章列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def getArticleList(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    list=[]
    list.append({
        'abstractContent': "Spring-data-redis是spring大家族的一部分，提供了在srping应用中通过简单的配置访问redis服务，对reids底层开发包(Jedis, JRedis, and RJC)进行了高度封装，RedisTemplate提供了redis各种操作、异常处理及序列化，支持发布订阅，并对spring 3.1 cache进行了实现。",
        'articleTags': [],
        'author': "tc",
        'category': {'id': 69, 'categoryCode': "", 'categoryName': "redis核心知识点", 'fullName': "", 'sort': "",
                     'parentId': ""},
        'categoryItems': "",
        'content': "",
        'coverImageList': ['http://file.miaoleyan.com/file/blog/UbQAfXZBobKC9c3rnKV8bO5lQDkzetTE'],
        'id': 69,
        'isRecommend': 0,
        'openComment': "",
        'publishTime': "2022022515",
        'showStyle': 1,
        'title': "RedisTemplate操作Redis",
        'viewCount': "",
    })
    bannn={"code":0,"data":{'currentPage': 1,'currentPageSize': 10,'rows': list,
'totalCount': 58,
'totalPage': 6}}
    # print(bannn)
    # banner = ujson.loads(bannn)


    return json(bannn)


@doc.summary('获取文章列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def getArticleList(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    list=[]
    list.append({
        'abstractContent': "Spring-data-redis是spring大家族的一部分，提供了在srping应用中通过简单的配置访问redis服务，对reids底层开发包(Jedis, JRedis, and RJC)进行了高度封装，RedisTemplate提供了redis各种操作、异常处理及序列化，支持发布订阅，并对spring 3.1 cache进行了实现。",
        'articleTags': [],
        'author': "tc",
        'category': {'id': 69, 'categoryCode': "", 'categoryName': "redis核心知识点", 'fullName': "", 'sort': "",
                     'parentId': ""},
        'categoryItems': "",
        'content': "",
        'coverImageList': ['http://file.miaoleyan.com/file/blog/UbQAfXZBobKC9c3rnKV8bO5lQDkzetTE'],
        'id': 69,
        'isRecommend': 0,
        'openComment': "",
        'publishTime': "2022022515",
        'showStyle': 1,
        'title': "RedisTemplate操作Redis",
        'viewCount': "",
    })
    bannn={"code":0,"data":{'currentPage': 1,'currentPageSize': 10,'rows': list,
'totalCount': 58,
'totalPage': 6}}
    # print(bannn)
    # banner = ujson.loads(bannn)


    return json(bannn)