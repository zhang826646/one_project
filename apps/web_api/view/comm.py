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


@doc.summary('banner')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def getBannerList(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    list=[]
    list.append({
        'author': "",
        'createOn': "2022-02-23",
        'id': 12,
        'imgSrc': "http://file.miaoleyan.com/file/blog/UbQAfXZBobKC9c3rnKV8bO5lQDkzetTE",
        'isDeleted': 0,
        'isShow': "",
        'linkUrl': "",
        'serialNumber': 1,
        'sortCode': "",
        'subTitle': "",
        'title': "温暖🍁",
        'updateOn': "2022-02-23",
    })
    bannn={"code":0,"data":{"rows":list,"currentPage":1,"totalPage":1,"currentPageSize":10,"totalCount":9}}
    # print(bannn)
    # banner = ujson.loads(bannn)


    return json(bannn)
