
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
        'type'          : doc.Integer('类型[1技术|2生活]'),
        'search_field'  : doc.String('搜索字段[id:帖子ID|uid:发帖人id|title:标题|content:内容|created_at:发布时间]'),
        'search_keyword': doc.String('搜索值[created_at:"1569859200|1569945600"'),
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
    page = request.valid_data.get('page', 1)
    limit = request.valid_data.get('limit', 15)
    catalog_id = request.valid_data.get('catalog_id')
    _type = request.valid_data.get('type')
    search_field = request.valid_data.get('search_field')
    search_keyword = request.valid_data.get('search_keyword')

    offset = (page - 1) * limit
    lists = []

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    search_cond = True
    if search_keyword:
        if search_field == 'id':  # 搜索ID
            search_cond = and_(search_cond, CirclePost.id == to_int(search_keyword))
        elif search_field == 'uid':  # 搜索发帖人
            search_cond = and_(search_cond, CirclePost.uid == to_int(search_keyword))
        elif search_field == 'title':  # 搜索标题
            search_cond = and_(search_cond, CirclePost.title.like(f'%{search_keyword}%'))
        elif search_field == 'content':  # 搜索内容
            search_cond = and_(search_cond, CirclePost.content.like(f'%{search_keyword}%'))
        elif search_field == 'created_at':
            created_at = search_keyword.split('|')
            if len(created_at) != 2:
                created_at = [0, 0]
            search_cond = CirclePost.created_at.between(to_int(created_at[0], 0), to_int(created_at[1], 0))

    if catalog_id:
        catalog_id_cond = CirclePost.catalog_id == catalog_id
    else:
        catalog_id_cond = True

    cond = and_(search_cond, catalog_id_cond)

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
            'title'            : row.CirclePost.title,
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


    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        # 'total'       : total,
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
    article_id = request.valid_data.get('article_id')
    title = request.valid_data.get('title')
    article_type = request.valid_data.get('type')
    tag = request.valid_data.get('tag')
    uid = request.valid_data.get('uid')
    content_compiled = request.valid_data.get('content_compiled')
    catalog_id = request.valid_data.get('catalog_id')
    summary = request.valid_data.get('summary')
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
