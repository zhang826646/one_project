
import re
import ujson
import random
import time
import lxml.html
from sanic.exceptions import InvalidUsage
from sanic.response import json
from sanic_openapi import doc
from sqlalchemy import and_, func
from sqlalchemy.orm import aliased
from common.exceptions import ApiError, ApiCode
from common.libs.comm import total_number, now, to_int, inc_count
from common.libs.aio import run_sqlalchemy
from common.helper.validator_helper import validate_params, CharField, IntegerField, ListField, DictField
from common.dao.circle import CirclePost
from common.dao.member import TtmMember


@doc.summary('帖子列表')
@doc.consumes(
    doc.JsonBody({
        'page'          : doc.Integer('页码'),
        'limit'         : doc.Integer('每页条数'),
        'catalog_id'    : doc.Integer('版块ID'),
        'postName'      : doc.String('帖子标题'),
        'status'  : doc.String('状态'),
    }), content_type='application/json', location='body', required=True
)
@validate_params(
    IntegerField(name='page', required=False, min_value=1),
    IntegerField(name='limit', required=False, min_value=1),
    IntegerField(name='catalog_id', required=False),
    # IntegerField(name='type', required=False, min_value=0, max_value=4),
    CharField(name='search_field', required=False),
    CharField(name='search_keyword', required=False),
)
async def article_list(request):
    page = request.json.get('pageNum', 1)
    limit = request.json.get('pageSize', 15)
    a_id = request.json.get('postCode')
    title = request.json.get('postName')
    status = request.json.get('status')


    offset = (page - 1) * limit
    lists = []

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    cond = True

    if a_id:
        cond = CirclePost.id == a_id
    if title:
        cond = CirclePost.title.like(f'%{title}%')
    if status:
        cond = CirclePost.deleted == status



    # cond = and_(cond, CirclePost.type != 1)

    @run_sqlalchemy()
    def get_post_list_data(db_session):
        return db_session.query(CirclePost, TtmMember) \
            .outerjoin(TtmMember, TtmMember.id == CirclePost.uid) \
            .filter(cond) \
            .order_by(CirclePost.created_at.desc()) \
            .offset(offset).limit(limit) \
            .all()

    rows = await get_post_list_data(ttm_sql)

    for row in rows:

        lists.append({
            'id'               : row.CirclePost.id,
            'catalog_id'       : row.CirclePost.catalog_id,
            'type'             : row.CirclePost.type if row.CirclePost.type != 4 else 0,
            'uid'              : row.CirclePost.uid,
            'name'             : row.TtmMember.name,
            'avatar'           : f'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'level'            : row.TtmMember.level,
            'banned'           : row.TtmMember.banned,
            'vip'              : row.TtmMember.vip_expire_at > now(),
            'title'            : row.CirclePost.title[:16]+'...' if len(row.CirclePost.title) > 16 else row.CirclePost.title ,
            'content'          : row.CirclePost.content,
            'deleted'          : row.CirclePost.deleted,
            'locked'           : row.CirclePost.locked,
            'picked'           : row.CirclePost.picked,
            'hidden'           : row.CirclePost.hidden,
            'total_comments'   : row.CirclePost.total_comments,
            'total_attachments': row.CirclePost.total_attachments,
            'attachments'      : '',
            'created_at'       : row.CirclePost.created_at,
            'visited'          : '0|0',
        })

    total = ttm_sql.query(func.count(CirclePost.id)).filter(cond).scalar()
    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'total'       : total,
        'data'        : lists
    }
    return json(data)

@doc.summary('编辑帖子')
@doc.consumes(
    doc.JsonBody({
        'article_id'         : doc.Integer('帖子ID'),
        'title'           : doc.String('帖子标题'),
        'type'            : doc.Integer('帖子类型 0普通贴 4比赛贴'),
        'tag'             : doc.String('标签'),
        'uid'             : doc.Integer('用户ID'),
        'content_compiled': doc.String('帖子内容 HTML'),
        'catalog_id'      : doc.Integer('版块ID'),
        'summary'         : doc.String('简介'),
    }), content_type='application/json', location='body', required=True
)
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
}, content_type='application/json', description='Request True')
@validate_params(
    IntegerField(name='article_id', required=False),
    CharField(name='title', allow_empty=True),
    IntegerField(name='type', required=False),
    CharField(name='tag', allow_empty=True),
    IntegerField(name='uid'),
    CharField(name='content_compiled', allow_empty=False),
    IntegerField(name='catalog_id'),
    CharField(name='summary', required=False),

)
async def save_article(request):
    article_id = request.json.get('article_id')
    title = request.json.get('title')
    article_type = request.json.get('type')
    tag = request.json.get('tag')
    uid = request.json.get('uid')
    content_compiled = request.json.get('content_compiled')
    catalog_id = request.json.get('catalog_id')
    summary = request.json.get('summary')
    atta_key = []

    async def _decompile_content(compiled):
        """
        将帖子内容 HTML <img> 标签  反编译为图片字段与内容字段
        :param compiled:
        :return:
        """
        attachment_no = 1
        atta_list = []

        def _repl(match):
            nonlocal attachment_no
            text = match.group(0)
            data_attributes = {x: y for (x, y) in re.findall(r'(data-[^=]+)="([^"]+)"', text)}

            if 'data-key' in data_attributes and 'data-mime-type' in data_attributes and \
                    'data-width' in data_attributes and 'data-height' in data_attributes:
                # 有data-xxx 字段直接取出返回
                key = data_attributes['data-key']
                mime_type = data_attributes['data-mime-type']
                width = data_attributes['data-width']
                height = data_attributes['data-height']
                atta_list.append(f'p{attachment_no}#{key}#{mime_type}#{width}#{height}')
                atta_key.append(key)
                replacement = '{{p%s}}' % attachment_no
                attachment_no = attachment_no + 1
                return replacement
            # else:
            #     # 没有 data-xxx 字段 取<img> src标签 上传到七牛云并获取宽、高、类型记录
            #     src_match = re.search(r'src="([^"]+)"', text)
            #     if not src_match:
            #         return ''
            #     url = src_match.group(1)
            #     url = re.sub(r'\?.*', '', url)
            #
            #     fetch_result = qiniu_helper.sync_fetch(url, path=f'attachment/{datetime.now().strftime("%Y/%m/%d/")}')
            #
            #     if fetch_result:
            #         key = fetch_result['key']
            #         mime_type = fetch_result['mimeType']
            #         composed_url = f'{cdn_url}{key}?imageInfo'
            #         res = requests.get(composed_url)
            #         if res.status_code == 200:
            #             width = res.json()['width']
            #             height = res.json()['height']
            #             atta_list.append(f'p{attachment_no}#{key}#{mime_type}#{width}#{height}')
            #             replacement = '{{p%s}}' % attachment_no
            #             attachment_no = attachment_no + 1
            #             return replacement
            #         else:
            #             return ''
        contents = re.sub(r'<img[^>]+>', _repl, compiled)
        return lxml.html.fromstring(contents).text_content(), '|'.join(atta_list), len(atta_list)
    content, attachments, total_attachments = await _decompile_content(content_compiled)

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    if article_id:
        item = ttm_sql.query(CirclePost).filter(CirclePost.id == article_id).first()
    else:
        item = CirclePost()
        item.created_at = item.last_replied_at = now()
        item.type = 0  # 类型[1技术|2生活]
        ttm_sql.add(item)

    item.title = title
    item.type = article_type
    item.content = content
    item.tag = tag
    item.uid = uid
    item.attachments = attachments
    item.catalog_id = catalog_id

    ttm_sql.flush()
    ttm_sql.commit()

    # if not article_id:
    #     redis_normal_5 = await request.app.leisu.get_redis('normal', db=5)
    #     @run_sqlalchemy()
    #     def get_total_posts_count(db_session):
    #         return db_session.query(func.count(CirclePost.id)).filter(CirclePost.uid == uid).scalar()
    #
    #     count = await get_total_posts_count(ttm_sql)
    #     await redis_normal_5.setex(f's:user_counter:group_posts:{uid}', 86400 * 30, count)  # 重新保存用户的发帖数
    #     await request.app.leisu.celery.send_task('apps.tasks.group.on_group_post_insert', args=(item.id,))  # 帖子创建触发任务
    # await request.app.leisu.celery.send_task('apps.tasks.group.on_group_post_change', args=(item.id,), kwargs={'delete_file': True})  # 触发帖子更新任务
    #
    # user = await get_member_cache(request.app, uid)
    # # 编辑帖子刷新cdn
    # if article_id:
    #     # refresh_url = f'https://app-gateway.leisu.com/v1/app/group/get_post?article_id={article_id}'
    #     refresh_url_2 = f'https://app-gateway.leisuapi.com/v1/app/group/get_post?article_id={article_id}'
    #     # await request.app.leisu.celery.send_task('apps.tasks.common.cdn_refresh', args=(refresh_url,), countdown=10)
    #     await request.app.leisu.celery.send_task('apps.tasks.common.cdn_refresh', args=(refresh_url_2,), countdown=10)


    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功', 'data': {'id': item.id}})


@doc.summary('帖子详情')
async def article_detali(request, article_id):
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    @run_sqlalchemy()
    def get_post_detail_data(db_session):
        return db_session.query(CirclePost, TtmMember) \
            .join(TtmMember, CirclePost.uid == TtmMember.id) \
            .filter(CirclePost.id == article_id) \
            .first()

    row = await get_post_detail_data(ttm_sql)
    if not row:
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='查无此帖')

    data = {
        'id'               : row.CirclePost.id,
        'title'            : row.CirclePost.title,
        'content'          : row.CirclePost.content,
        'type'             : row.CirclePost.type if row.CirclePost.type != 4 else 0,  # 比赛贴转为普通贴
        'attachments'      : row.CirclePost.attachments,
        'total_attachments': row.CirclePost.total_attachments,
        'catalog_id'       : row.CirclePost.catalog_id,
        # 'catalog_name'     : group_catalogs[row.CirclePost.catalog_id % 100]['name'],
        'tag'              : row.CirclePost.tag,
        'catalog_name'      :'',
        'uid'              : row.CirclePost.uid,
        'name'             : row.TtmMember.name,
        # 'avatar'           : f'{cdn_url}user/avatar/{row.TtmMember.avatar}' if row.TtmMember else '',
        'avatar':f'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        'level'            : row.TtmMember.level,
        'banned'           : row.TtmMember.banned,
        'vip'              : row.TtmMember.vip_expire_at > now(),
        'deleted'          : row.CirclePost.deleted,
        'locked'           : row.CirclePost.locked,
        'picked'           : row.CirclePost.picked,
        'hidden'           : row.CirclePost.hidden,
        'total_comments'   : row.CirclePost.total_comments,
        'total_floors'     : row.CirclePost.total_floors,
        'created_at'       : row.CirclePost.created_at,
    }
    return json({'code': ApiCode.SUCCESS, 'data': data})


@doc.summary('删除帖子')
@validate_params(
    ListField(name='post_id_list'),
    IntegerField(name='deleted', min_value=0, max_value=1),
    CharField(name='reason', required=False)
)
async def delete_article(request):
    post_id_list = request.json.get('post_id_list')
    deleted = request.json.get('deleted')
    reason = request.json.get('reason', '')
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    posts = ttm_sql.query(CirclePost).filter(CirclePost.id.in_(post_id_list)).all()
    for post in posts:
        post.deleted = deleted

    ttm_sql.commit()
    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})