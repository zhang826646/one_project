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


@doc.summary('主页')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
@mako.template('index.html')
async def index(request):

    new_time=datetime.datetime.fromtimestamp(1636366351)
    data={'data':[{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','urls':'http://www.sssoou.com','tags':[{'name':'技术','urls':'https://www.baidu.com'}]},{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','urls':'http://www.sssoou.com','tags':[{'name':'技术','urls':'https://www.baidu.com'}]}]}
    # data={'users':[{'name':'user1'},{'name':'user2'},{'name':'user3'},{'name':'user4'},{'name':'user5'},{'name':'user6'}]}
    return data
    # return json(data)


@doc.summary('主页1')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def index1(request):
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    @run_sqlalchemy()
    def get_circles(db_session):
        return db_session.query(CirclePost).filter().order_by(CirclePost.created_at.desc()).limit(20).all()

    item = []
    for row in await get_circles(ttm_sql):
        item.append({
            'id': row.id,
            'catalog_id': row.catalog_id,
            'type': row.type,
            'title': row.title,
            'content': row.content,
            'total_comments': row.total_comments,
            'attachments': row.attachments,
            'created_at': row.created_at,

        })
    return json({
        'code': 0,
        'msg': '',
        'data': item
    })

@doc.summary('查看文章详情')
@doc.consumes(
    doc.JsonBody({
        'post_id': doc.String('用户名'),
    }), content_type='application/json', location='body', required=True
)
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def cat_post(request,post_id):
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    # circle= ttm_sql.query(CirclePost).filter(CirclePost.id == post_id).first()
    #
    # if not circle:
    #     raise ApiError(code=ApiCode.PARAM_ERR, msg='文章不存在')

    def compile_content(content, attachments):
        """
        将帖子内容与图片编码为HTML
        :param content: 帖子内容
        :param attachments: 帖子图片 p1#group/attachments/FqXPGSso5Kf3PmtBR2RBkPmkytRJ#image/jpeg#828#1792
        :return: HTML <img> 标签
        """
        attachments_dict = {}
        if attachments:
            attachments_list = attachments.split('|')
            for _item in attachments_list:
                attachment_data = _item.split('#')
                if attachment_data[1] != 'None':
                    attachments_dict[attachment_data[0]] = attachment_data

        def repl(word):
            name = word.group(1)
            if name in attachments_dict:
                url = ''
                key = attachments_dict[name][1]
                mime_type = attachments_dict[name][2]
                width = attachments_dict[name][3]
                height = attachments_dict[name][4]
                return f'<img src="{url}" class="attachment" data-key="{key}" ' \
                       f'data-mime-type="{mime_type}" data-width="{width}" data-height="{height}">'
            return ''

        compiled = re.sub(r'{{([^}]*)}}', repl, content)  # 替换{{p1}} 为img标签
        compiled = re.sub(r'([^\r\n]*)?(\r\n|\r|\n)?', '<p>\g<1></p>', compiled)  # 替换回车为 </br>
        return compiled

    @run_sqlalchemy()
    def get_post_detail_data(db_session):
        return db_session.query(CirclePost, TtmMember) \
            .join(TtmMember, CirclePost.uid == TtmMember.id) \
            .filter(CirclePost.id == post_id) \
            .first()

    row = await get_post_detail_data(ttm_sql)
    if not row:
        raise ApiError(code=ApiCode.NORMAL_ERR, msg='查无此帖')

    data = {
        'id': row.CirclePost.id,
        'title': row.CirclePost.title,
        'content': row.CirclePost.content,
        'content_compiled': compile_content(row.CirclePost.content, row.CirclePost.attachments),
        'type': row.CirclePost.type if row.CirclePost.type != 4 else 0,  # 比赛贴转为普通贴
        'attachments': row.CirclePost.attachments,
        'total_attachments': row.CirclePost.total_attachments,
        'catalog_id': row.CirclePost.catalog_id,
        'catalog_name': 1,
        'tag': row.CirclePost.tag,
        'uid': row.CirclePost.uid,
        'name': row.TtmMember.name,
        'avatar': '',
        'level': row.TtmMember.level,
        'banned': row.TtmMember.banned,
        'vip': row.TtmMember.vip_expire_at > now(),
        'annual_vip': row.TtmMember.annual_vip_expire_at > now(),
        'extra': ujson.loads(row.TtmMember.extra) if row.TtmMember.extra else {},
        'deleted': row.CirclePost.deleted,
        'locked': row.CirclePost.locked,
        'picked': row.CirclePost.picked,
        'hidden': row.CirclePost.hidden,
        'total_comments': row.CirclePost.total_comments,
        'total_floors': row.CirclePost.total_floors,
        'created_at': row.CirclePost.created_at,
        'params': ujson.loads(row.CirclePost.params) if row.CirclePost.params else {}
    }
    return json({'code': ApiCode.SUCCESS, 'data': data})


@doc.summary('编辑帖子')
@doc.consumes(
    doc.JsonBody({
        'post_id'         : doc.Integer('帖子ID'),
        'title'           : doc.String('帖子标题'),
        'type'            : doc.Integer('类型[1技术|2生活]'),
        'tag'             : doc.String('标签'),
        'uid'             : doc.Integer('用户ID'),
        'content_compiled': doc.String('帖子内容 HTML'),
        'catalog_id'      : doc.Integer('版块ID'),

    }), content_type='application/json', location='body', required=True
)
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
}, content_type='application/json', description='Request True')
async def save_post(request):
    post_id = request.valid_data.get('post_id')
    title = request.valid_data.get('title','测试数据')
    post_type = request.valid_data.get('type',1)
    tag = request.valid_data.get('tag','测试')
    uid = request.valid_data.get('uid',1000000)
    catalog_id = request.valid_data.get('catalog_id',1)

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    # group_catalogs = await get_group_catalogs(request.app)  #获取板块
    atta_key = []

    # async def _decompile_content(compiled):
    #     """
    #     将帖子内容 HTML <img> 标签  反编译为图片字段与内容字段
    #     :param compiled:
    #     :return:
    #     """
    #     attachment_no = 1
    #     atta_list = []
    #
    #     def _repl(match):
    #         nonlocal attachment_no
    #         text = match.group(0)
    #         data_attributes = {x: y for (x, y) in re.findall(r'(data-[^=]+)="([^"]+)"', text)}
    #
    #         if 'data-key' in data_attributes and 'data-mime-type' in data_attributes and \
    #                 'data-width' in data_attributes and 'data-height' in data_attributes:
    #             # 有data-xxx 字段直接取出返回
    #             key = data_attributes['data-key']
    #             mime_type = data_attributes['data-mime-type']
    #             width = data_attributes['data-width']
    #             height = data_attributes['data-height']
    #             atta_list.append(f'p{attachment_no}#{key}#{mime_type}#{width}#{height}')
    #             atta_key.append(key)
    #             replacement = '{{p%s}}' % attachment_no
    #             attachment_no = attachment_no + 1
    #             return replacement
    #         else:
    #             # 没有 data-xxx 字段 取<img> src标签 上传到七牛云并获取宽、高、类型记录
    #             src_match = re.search(r'src="([^"]+)"', text)
    #             if not src_match:
    #                 return ''
    #             urls = src_match.group(1)
    #             urls = re.sub(r'\?.*', '', urls)
    #
    #             fetch_result = qiniu_helper.sync_fetch(urls, path=f'attachment/{datetime.now().strftime("%Y/%m/%d/")}')
    #
    #             if fetch_result:
    #                 key = fetch_result['key']
    #                 mime_type = fetch_result['mimeType']
    #                 composed_url = f'{cdn_url}{key}?imageInfo'
    #                 res = requests.get(composed_url)
    #                 if res.status_code == 200:
    #                     width = res.json()['width']
    #                     height = res.json()['height']
    #                     atta_list.append(f'p{attachment_no}#{key}#{mime_type}#{width}#{height}')
    #                     replacement = '{{p%s}}' % attachment_no
    #                     attachment_no = attachment_no + 1
    #                     return replacement
    #                 else:
    #                     return ''
    #     contents = re.sub(r'<img[^>]+>', _repl, compiled)
    #     return lxml.html.fromstring(contents).text_content(), '|'.join(atta_list), len(atta_list)
    # content, attachments, total_attachments = await _decompile_content(content_compiled)
    content='这是测试数据-内容，这是测试数据-内容，这是测试数据-内容，这是测试数据-内容，这是测试数据-内容，'
    attachments=''
    if not post_id:
        item = CirclePost()
        item.created_at = item.last_replied_at = now()
        item.type = 0   # [0:普通帖子|1:互动贴]
        ttm_sql.add(item)
    else:
        item = ttm_sql.query(CirclePost).filter(CirclePost.id == post_id).first()
    item.title = title
    item.type = post_type
    item.content = content
    item.tag = tag
    item.uid = uid
    item.attachments = attachments
    item.catalog_id = catalog_id
    # ttm_sql.flush()
    ttm_sql.commit()


    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功', 'data': {'id': item.id}})