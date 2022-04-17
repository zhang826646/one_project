from sanic_openapi import doc
from sanic.response import json
from apps import mako,render_template
from typing import Dict, List, Tuple, Union
from sqlalchemy import and_,or_
import datetime
import re
import ujson
from common.dao.circle import CirclePost,CircleCatalog
from common.dao.member import TtmMember
from common.exceptions import ApiError,ApiCode
from common.libs.aio import run_sqlalchemy
from common.libs.comm import now,total_number
from apps import mako
import time


@doc.summary('获取文章列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def getArticleList(request):
    page = request.valid_data.get('pageIndex', 1)
    limit = request.valid_data.get('pageSize', 15)
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    offset = (page - 1) * limit

    @run_sqlalchemy()
    def get_post_data(db_session):
        return db_session.query(CirclePost, TtmMember,CircleCatalog) \
            .join(TtmMember, CirclePost.uid == TtmMember.id) \
            .join(CircleCatalog, CirclePost.catalog_id == CircleCatalog.id) \
            .offset(offset).limit(limit) \
            .all()

    rows = await get_post_data(ttm_sql)

    list = []
    for row in rows:
        item={
            'id': row.CirclePost.id,
            'title': row.CirclePost.title,
            'abstractContent': row.CirclePost.content,
            'articleTags': row.CirclePost.tag,
            'author': "tc",
            'category': {'id': row.CircleCatalog.id,
                         'categoryCode': "",
                         'categoryName': row.CircleCatalog.catalog_name,
                         'fullName': "",
                         'sort': "",
                         'parentId': ""},
            'categoryItems': "",
            'content': "",
            'coverImageList': ['http://file.miaoleyan.com/file/blog/UbQAfXZBobKC9c3rnKV8bO5lQDkzetTE'],
            'isRecommend': 0,
            'openComment': "",
            'publishTime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(row.CirclePost.created_at)),
            'showStyle': 1,
            'viewCount': "",
        }
        list.append(item)

    totalCount = await total_number(ttm_sql, CirclePost.id)
    return json({
        "code": 0,
        "data": {
            'currentPage': page,
            'currentPageSize': limit,
            'rows': list,
            'totalCount': totalCount,
            'totalPage': totalCount//totalCount
        }
    })


@doc.summary('获取标签列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def getTagList(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    @run_sqlalchemy()
    def get_catalog_data(db_session):
        return db_session.query(CircleCatalog).all()

    rows = await get_catalog_data(ttm_sql)
    list=[]
    for row in rows:
        list.append({
            'id': row.id,
            'alia': row.catalog_name,
            'color': "#EB6841",
            'value': row.catalog_name,
        })

    return json({"code":0,'data': list,})



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