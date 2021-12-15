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
    data={'data':[{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]},{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]}]}
    # data={'users':[{'name':'user1'},{'name':'user2'},{'name':'user3'},{'name':'user4'},{'name':'user5'},{'name':'user6'}]}
    return data
    # return json(data)

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


# @doc.summary('发布文章')
# @doc.produces({
#     'code': doc.Integer('状态码'),
#     'msg' : doc.String('消息提示'),
#     'data': {'token': doc.String('Token')}
# }, content_type='application/json', description='Request True')
# @mako.template('index.html')
# async def index(request):
#
#     new_time=datetime.datetime.fromtimestamp(1636366351)
#     data={'data':[{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]},{'title':'zhang','created_at':new_time,'excerpt':'这只是测试的一条数据','url':'http://www.sssoou.com','tags':[{'name':'技术','url':'https://www.baidu.com'}]}]}
#     # data={'users':[{'name':'user1'},{'name':'user2'},{'name':'user3'},{'name':'user4'},{'name':'user5'},{'name':'user6'}]}
#     return data
#     # return json(data)