from sanic_openapi import doc
from sanic.response import json
# from apps import mako,render_template
from typing import Dict, List, Tuple, Union
from sqlalchemy import and_,or_
import datetime
import re
from sqlalchemy.sql.operators import *
from common.libs.tokenize_util import encrypt_web_token,decrypt_web_token
import urllib
import ujson
from common.dao.circle import CirclePost,CircleCatalog,CircleComment
from common.dao.member import TtmMember
from common.exceptions import ApiError,ApiCode
from common.libs.aio import run_sqlalchemy
from common.libs.comm import now,total_number,to_strtime
from apps.comm.message import create_message
# from apps import mako
import time


@doc.summary('获取文章列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def getArticleList(request):
    page = request.json.get('pageIndex', 1)
    limit = request.json.get('pageSize', 15)
    tag = request.json.get('tag')
    is_me = request.json.get('is_me')
    search_title = request.json.get('title')

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    offset = (page - 1) * limit

    cond = CirclePost.deleted == 0
    if tag:
        cond = and_(cond,CirclePost.catalog_id == tag)
    if is_me:
        token = request.cookies.get('Ttm-Token')
        if not token:
            raise ApiError(code=0, msg='请先登录')
        token = urllib.parse.unquote(token)
        user_info = decrypt_web_token(token)
        uid = user_info.get('uid')
        print(uid,type(uid))
        cond = and_(cond,CirclePost.uid == uid)
    else:
        cond = and_(cond, CirclePost.hidden == 0)
    if search_title:
        cond = and_(cond, CirclePost.title.like(f'%{search_title}%'))


    @run_sqlalchemy()
    def get_post_data(db_session):
        return db_session.query(CirclePost, TtmMember,CircleCatalog) \
            .join(TtmMember, CirclePost.uid == TtmMember.id) \
            .join(CircleCatalog, CirclePost.catalog_id == CircleCatalog.id) \
            .filter(cond) \
            .order_by(CirclePost.created_at.desc()) \
            .offset(offset).limit(limit) \
            .all()

    rows = await get_post_data(ttm_sql)

    list = []
    for row in rows:
        content=row.CirclePost.content
        coverImageList = ['http://cdn.qxiaolu.club/banner/banner.png']
        if row.CirclePost.type == 2:
            src_match = re.search(r'src="([^"]+)"', content)
            print(src_match )
            if src_match:
                # 首页图片处理
                coverImageList = [src_match.group(1)]
                url = re.sub(r'\?.*', '', src_match.group(1))
                print(src_match.group(1),url)
                content= content.replace(src_match.group(1),'')
            # 标签处理
            re_h = re.compile('</?\w+[^>]*>')  # HTML标签
            content = re_h.sub('', content)  # 去掉HTML 标签
            # content = re.sub(f'{coverImageList}','', wait_comtent)
        else:
            content= content[:200]

        item={
            'id': row.CirclePost.id,
            'uid':row.CirclePost.uid,
            'title': row.CirclePost.title,
            'deleted': row.CirclePost.deleted,
            'hidden': row.CirclePost.hidden,
            'abstractContent': content,
            'articleTags': row.CirclePost.tag,
            'author': row.TtmMember.name,
            'category': {'id': row.CircleCatalog.id,
                         'categoryCode': "",
                         'categoryName': row.CircleCatalog.catalog_name,
                         'fullName': "",
                         'sort': "",
                         'parentId': ""},
            'categoryItems': "",
            'content': "",
            'coverImageList': coverImageList,
            'isRecommend': 0,
            'openComment': "",
            'publishTime': to_strtime(row.CirclePost.created_at),
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
            'totalPage': totalCount//limit + 1
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
            'name': row.catalog_name,
            'color': "#EB6841",
            'value' : row.id,
            'label' : row.catalog_name,
        })

    return json({"code":0,'data': list,})



@doc.summary('获取推荐文章列表')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def getRecommendArticleList(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    @run_sqlalchemy()
    def get_post_data(db_session):
        return db_session.query(CirclePost, TtmMember,CircleCatalog) \
            .join(TtmMember, CirclePost.uid == TtmMember.id) \
            .join(CircleCatalog, CirclePost.catalog_id == CircleCatalog.id) \
            .filter(CirclePost.picked == 1) \
            .limit(10) \
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
            'publishTime': to_strtime(row.CirclePost.created_at),
            'showStyle': 1,
            'viewCount': "",
        }
        list.append(item)
    # list=[]
    # list.append({
    #     'abstractContent': "Redis实例默认建立了16个db库，由于不支持自主进行数据库命名所以以dbX的方式命名。默认数据库数量可以修改配置文件的database值来设定。每个db可以理解为“命名空间”，客户端应用可以使用不同的db来存储不同环境的数据。客户端如果没有执行db编号，默认为编号为0的db。最后要注意，Redis集群下只有db0，不支持多db。\n\nRedis的数据都存放在内存中，如果redis服务突然宕机，会造成数据的丢失。为了保证数据的灾难性恢复，redis提供了两种持久化模式，一种是RDB快照（snapshotting），默认开启，另外一种是AOF（append-only-file），默认未开启。",
    #     'articleTags': "7",
    #     'articleType': 0,
    #     'author': "tc",
    #     'category': {},
    #     'categoryCode': "0001",
    #     'categoryId': 1,
    #     'coverImageList': [{}],
    #     'createTime': "2021-11-08",
    #     'disPlayStatus': "published",
    #     'editorType': 0,
    #     'id': 51,
    #     'isRecommend': 1,
    #     'publishTime': "2021-11-07 23:47:19",
    #     'showStyle': 1,
    #     'status': 1,
    #     'statusAliaName': "已发布",
    #     'title': "redis持久化机制🍂",
    #     'updateTime': "2021-11-08",
    # })
    bannn={"code":0,'data': list,}
    # print(bannn)
    # banner = ujson.loads(bannn)


    return json(bannn)


@doc.summary('文章详情')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def getArticleDetail(request,article_id):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    print('++++++++',article_id)

    @run_sqlalchemy()
    def get_post_data(db_session):
        return db_session.query(CirclePost, TtmMember,CircleCatalog) \
            .outerjoin(TtmMember, TtmMember.id == CirclePost.uid ) \
            .outerjoin(CircleCatalog,CircleCatalog.id == CirclePost.catalog_id) \
            .filter(CirclePost.id == article_id) \
            .first()

    row = await get_post_data(ttm_sql)
    print(row)
    if not row :
        raise ApiError( msg='文章不存在')

    item =  {
        "id": row.CirclePost.id,
        "title": row.CirclePost.title,
        "abstractContent": "",
        "publishTime": to_strtime(row.CirclePost.created_at),
        'member_id': row.CirclePost.uid,
        "categoryItems": "",
        "articleTags": row.CirclePost.tag,
        "showStyle": 1,
        "coverImageList": [
            "http://cdn.qxiaolu.club/banner/baner2.png"],
        "openComment": 1,
        "isRecommend": 1,
        "author": row.TtmMember.name,
        "viewCount": "",
        "category": {"id": 73,
                     "categoryCode": "",
                     "categoryName": "",
                     "fullName": "",
                     "sort": "",
                     "parentId": "",
                     "isParent": "",
                     "path": "",
                     "level": "",
                     "status": 1,
                     "createOn": "", "updateOn": ""},
        "content": row.CirclePost.content
    }

    bannn={"code":0,'data': item,}

    return json(bannn)


@doc.summary('评论详情')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def getArticleComment(request,article_id):
    # print(request.__dict__)
    # article_id = request.json.get('article_id')
    print(article_id)
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    @run_sqlalchemy()
    def get_post_data(db_session):
        return db_session.query(CircleComment, TtmMember) \
            .join(TtmMember, CircleComment.uid == TtmMember.id) \
            .filter(CircleComment.post_id == article_id) \
            .limit(10) \
            .all()

    rows = await get_post_data(ttm_sql)
    user_ids=[x.CircleComment.to_uid for x in rows]

    @run_sqlalchemy()
    def get_member_data(db_session):
        return db_session.query(TtmMember) \
            .filter(TtmMember.id.in_(user_ids)) \
            .all()

    member_rows = await get_member_data(ttm_sql)
    member_dict={i.id:i.name for i in member_rows}
    print(member_dict)

    _comment_list = []
    reply_list_dict = {}


    comment_id_list = []
    comment_like_dict = {}


    for row in rows:
        comment_id_list.append(row.CircleComment.id)


        if row.CircleComment.parent_id == 0:
            comment_item = {
                'id'               : row.CircleComment.id,
                'floor'            : row.CircleComment.floor,
                'content'          : row.CircleComment.content,
                'createtime'       : to_strtime(row.CircleComment.created_at),
                'uid'              : row.CircleComment.uid,
                'usernickname'             : row.TtmMember.name if row.TtmMember else '',
                'tousernickname' :member_dict.get( row.CircleComment.uid),
                'useravatar'           : f'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
                'total_attachments': row.CircleComment.total_attachments,
                'total_replies'    : row.CircleComment.total_replies,
                'like'             : 0,
                'replylist'      : [],
                'isshownew': '',
                'emojishow': '',
            }
            _comment_list.append(comment_item)
        else:

            reply_item = {
                'id'               : row.CircleComment.id,
                'floor'            : row.CircleComment.floor,
                'content'          : row.CircleComment.content,
                'createtime'       : to_strtime(row.CircleComment.created_at),
                'uid'              : row.CircleComment.uid,
                'usernickname'             : row.TtmMember.name if row.TtmMember else '',
                'tousernickname': member_dict.get(row.CircleComment.uid),
                'useravatar'           : f'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
                'total_attachments': row.CircleComment.total_attachments,
                'like'             : 0,
            }
            if row.CircleComment.parent_id not in reply_list_dict:
                reply_list_dict[row.CircleComment.parent_id] = []
            reply_list_dict[row.CircleComment.parent_id].append(reply_item)
    _comment_list = sorted(_comment_list, key=lambda x: x['floor'], reverse=False)
    # # 绑定点赞数
    # if comment_id_list:
    #     comment_like_list = await redis_tair.hmget('h:group:comment_counter:like', *comment_id_list)
    #     comment_like_list = [to_int(x, 0) for x in comment_like_list]
    #     comment_like_dict = dict(zip(comment_id_list, comment_like_list))
    for comment_item in _comment_list:
        # comment_item['like'] = comment_like_dict.get(comment_item['id'])
        if comment_item['id'] in reply_list_dict:
            reply_list = reply_list_dict[comment_item['id']]
            reply_list = sorted(reply_list, key=lambda x: x['id'])
            print()
            # for reply_item in reply_list:
            #     reply_item['like'] = comment_like_dict.get(reply_item['id'])
            comment_item['replylist'] = reply_list
    print(_comment_list)
    return json({'code': 0, 'data': _comment_list})



@doc.summary('编辑、创建文章')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def saveArticle(request):
    print(request.json)
    article_id = request.json.get('id')
    member_id = request.json.get('member_id')
    author = request.json.get('author')
    title = request.json.get('title')
    isRecommend = request.json.get('isRecommend')
    openComment = request.json.get('openComment')
    abstractContent = request.json.get('abstractContent')
    articleTags = request.json.get('articleTags')

    catalog_id = request.json.get('catalog_id',0)
    content = request.json.get('content')
    coverImageList = request.json.get('coverImageList')
    showStyle = request.json.get('showStyle')
    status = request.json.get('status')
    title = request.json.get('title')

    token = request.cookies.get('Ttm-Token')
    if not token:
        raise ApiError(code=0 ,msg='请先登录')
    token= urllib.parse.unquote(token)
    user_info = decrypt_web_token(token)
    uid = user_info.get('uid')
    print(uid)

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')


    if not article_id:
        article=CirclePost()
        ttm_sql.add(article)
    else:
        article =ttm_sql.query(CirclePost).filter(CirclePost.id == article_id).first()
        if not article:
            raise ApiError(code=0,mag='文章不存在')
    article.type = 2
    article.title = title
    article.content = content
    article.catalog_id = catalog_id
    article.attachments = ujson.dumps(coverImageList,ensure_ascii=False)
    article.hidden = status
    article.tag = articleTags
    article.uid = uid or member_id
    article.created_at =now()

    ttm_sql.commit()

    data={
        'article_id' : article.id,
        'member_id'  : article.uid
    }
    return json({'code': 0,'data':data, 'mag':'保存成功'})


@doc.summary('删除隐藏文章')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def stateArticle(request):
    print(request.json)
    article_id = request.json.get('article_id')
    deleted = request.json.get('deleted')
    hidden = request.json.get('hidden')

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    article = ttm_sql.query(CirclePost).filter(CirclePost.id == article_id).first()
    if not article:
        raise ApiError(code=0,msg='文章不存在')

    article.deleted = deleted
    article.hidden = hidden

    ttm_sql.commit()

    return json({'code': 0, 'mag':'操作成功'})


@doc.summary('创建评论')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),

}, content_type='application/json', description='Request True')
async def addComment(request):
    print(request.json)
    token = request.cookies.get('Ttm-Token')
    print(token)

    if not token:
        raise ApiError(code=0,msg='请先登录')
    token= urllib.parse.unquote(token)
    user_info = decrypt_web_token(token)

    article_id = request.json.get('article_id')
    touseruuid= request.json.get('touseruuid')
    pid = request.json.get('pid')

    content = request.json.get('content')

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    if not article_id:
        raise ApiError(msg='参数错误')


    comment = CircleComment()
    comment.post_id = article_id
    comment.uid = user_info.get('uid')
    comment.to_uid = touseruuid if pid and touseruuid else user_info.get('uid')
    comment.parent_id = pid
    comment.content = content
    comment.created_at = now()
    ttm_sql.add(comment)
    ttm_sql.flush()

    ttm_sql.commit()

    await create_message(request.app, 2, comment.to_uid, comment_id=comment.id)

    return json({'code': 0, 'mag':'保存成功'})
