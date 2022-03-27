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
        'publishTime': "2022-02-25 15:00",
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


@doc.summary('获取标签列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def getTagList(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    list=[]
    list.append({
        'alia': "python",
        'color': "#EB6841",
        'id': "1",
        'value': "python",
    })
    bannn={"code":0,'data': list,}
    # print(bannn)
    # banner = ujson.loads(bannn)


    return json(bannn)



@doc.summary('获取推荐文章列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def getRecommendArticleList(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    list=[]
    list.append({
        'abstractContent': "Redis实例默认建立了16个db库，由于不支持自主进行数据库命名所以以dbX的方式命名。默认数据库数量可以修改配置文件的database值来设定。每个db可以理解为“命名空间”，客户端应用可以使用不同的db来存储不同环境的数据。客户端如果没有执行db编号，默认为编号为0的db。最后要注意，Redis集群下只有db0，不支持多db。\n\nRedis的数据都存放在内存中，如果redis服务突然宕机，会造成数据的丢失。为了保证数据的灾难性恢复，redis提供了两种持久化模式，一种是RDB快照（snapshotting），默认开启，另外一种是AOF（append-only-file），默认未开启。",
        'articleTags': "7",
        'articleType': 0,
        'author': "tc",
        'category': {},
        'categoryCode': "0001",
        'categoryId': 1,
        'coverImageList': [{}],
        'createTime': "2021-11-08",
        'disPlayStatus': "published",
        'editorType': 0,
        'id': 51,
        'isRecommend': 1,
        'publishTime': "2021-11-07 23:47:19",
        'showStyle': 1,
        'status': 1,
        'statusAliaName': "已发布",
        'title': "redis持久化机制🍂",
        'updateTime': "2021-11-08",
    })
    bannn={"code":0,'data': list,}
    # print(bannn)
    # banner = ujson.loads(bannn)


    return json(bannn)