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
from common.dao.book import Book
from common.dao.member import TtmMember
from common.dao.pay import PayRecord,TtmGoods


@doc.summary('交易列表')
async def record_list(request):
    page = request.json.get('pageNum', 1)
    limit = request.json.get('pageSize', 15)
    id = request.json.get('payid')
    username = request.json.get('username')
    beginTime = request.json.get('beginTime')
    endTime = request.json.get('endTime')



    offset = (page - 1) * limit
    lists = []

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    cond  = True

    if username:
        cond = Book.TtmMember.like(f'%{username}%')
    if id:
        cond = PayRecord.id == id

    if beginTime and endTime:
        cond=and_(cond,PayRecord.created_at.between(int(beginTime)//1000, int(endTime)//1000))

    @run_sqlalchemy()
    def get_pay_list_data(db_session):
        return db_session.query(PayRecord, TtmMember, TtmGoods) \
            .outerjoin(TtmMember,TtmMember.id == PayRecord.uid) \
            .outerjoin(TtmGoods, TtmGoods.id == PayRecord.goods_id) \
            .filter(cond) \
            .order_by(PayRecord.created_at.desc()) \
            .offset(offset).limit(limit) \
            .all()

    rows = await get_pay_list_data(ttm_sql)

    for row in rows:
        lists.append({
            'id'               : row.PayRecord.id,
            'alipay_order'       : row.PayRecord.alipay_order,
            'money'             : str(row.PayRecord.money) ,
            'count'              : row.PayRecord.count,
            'status'          : row.PayRecord.status,
            'created_at'          : row.PayRecord.created_at,

            'user_id'           :  row.TtmMember.id if row.TtmMember else 0,
            'user_name': row.TtmMember.name if row.TtmMember else '',

            'goods_id': row.TtmGoods.id if row.TtmGoods else 0,
            'goods_name': row.TtmGoods.goods_name if row.TtmGoods else '手动订单' ,

        })

    total = ttm_sql.query(func.count(PayRecord.id)).filter(cond).scalar()
    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'total'       : total,
        'data'        : lists
    }
    return json(data)


@doc.summary('交易列表')
async def goods_list(request):
    page = request.json.get('pageNum', 1)
    limit = request.json.get('pageSize', 15)
    # title = request.json.get('bookName')
    # _type = request.json.get('bookType')
    # status = request.json.get('status')

    beginTime = request.json.get('beginTime')
    endTime = request.json.get('endTime')



    offset = (page - 1) * limit
    lists = []

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    cond = True
    if beginTime and endTime:
        cond = and_(cond, TtmGoods.created_at.between(int(beginTime) // 1000, int(endTime) // 1000))
    # if title:
    #     cond = Book.title.like(f'%{title}%')
    # if _type:
    #     cond = and_(cond, Book.booktpye == _type)

    @run_sqlalchemy()
    def get_pay_list_data(db_session):
        return db_session.query(TtmGoods) \
            .filter(cond) \
            .order_by(TtmGoods.created_at.desc()) \
            .offset(offset).limit(limit) \
            .all()

    rows = await get_pay_list_data(ttm_sql)

    for row in rows:
        lists.append({
            'id'            : row.id,
            'goods_name'    : row.goods_name,
            'price'         : str(row.price),
            't_gold'        : row.t_gold,
            'goods_desc'    : row.goods_desc,
            'status'       : str(row.on_sale),
            'created_at'    : row.created_at,
        })

    total = ttm_sql.query(func.count(TtmGoods.id)).filter(cond).scalar()
    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'total'       : total,
        'data'        : lists
    }
    return json(data)



@doc.summary('编辑帖子')
async def save_goods(request):
    goods_id = request.json.get('id')
    goods_name = request.json.get('goods_name')
    sm_logo = request.json.get('sm_logo','')
    price = request.json.get('price')
    t_gold = request.json.get('t_gold')
    goods_desc = request.json.get('goods_desc','')
    on_sale = request.json.get('status',1)

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    if not price and not t_gold and not goods_name:
        raise ApiError(msg='请填写商品信息')

    if goods_id:
        item = ttm_sql.query(TtmGoods).filter(TtmGoods.id == goods_id).first()
        if not item:
            raise ApiError(msg='商品不存在')
    else:
        item = TtmGoods()
        item.created_at=now()
        ttm_sql.add(item)

    item.goods_name = goods_name
    if sm_logo:
        item.sm_logo = sm_logo
    item.price = price
    item.t_gold = t_gold
    item.goods_desc = goods_desc
    item.on_sale = on_sale

    ttm_sql.commit()


    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})


@doc.summary('编辑帖子')
async def pay_goods(request):
    user_id = request.json.get('user_id')
    t_gold = request.json.get('t_gold')


    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    if user_id:
        item = ttm_sql.query(TtmMember).filter(TtmMember.id == int(user_id)).first()
        if not item:
            raise ApiError(msg='用户不存在')

        item.money_nwdbl += int(t_gold)

        payrecord = PayRecord()
        payrecord.uid = user_id
        payrecord.goods_id = 0
        payrecord.alipay_order = 0
        payrecord.count = 1
        payrecord.money = int(t_gold)//10
        payrecord.status = 0
        payrecord.created_at = now()

        ttm_sql.add(payrecord)
        ttm_sql.commit()


        ttm_sql.commit()


    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})


@doc.summary('书籍详情')
@doc.consumes(
    doc.JsonBody({
        'page'          : doc.Integer('页码'),
        'limit'         : doc.Integer('每页条数'),
        'catalog_id'    : doc.Integer('版块ID'),
        'postName'      : doc.String('帖子标题'),
        'status'  : doc.String('状态'),
    }), content_type='application/json', location='body', required=True
)
async def book_detali(request,id):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    cond = Book.id == id

    @run_sqlalchemy()
    def get_book_data(db_session):
        return db_session.query(Book) \
            .filter(cond) \
            .first()

    row = await get_book_data(ttm_sql)


    item={
        'id'               : row.id,
        'title'       : row.title,
        'author'             : row.author ,
        'publish'              : row.publish,
        'booktpye'             : row.booktpye,
        'pages'          : row.pages,
        'book_url'          : row.book_url,
        'update_time'           : row.update_time,

    }

    data = {
        'code'        : ApiCode.SUCCESS,
        'data'        : item
    }
    return json(data)



@doc.summary('删除帖子')
async def delete_book(request):
    book_id_list = request.json.get('book_id_list')
    print(book_id_list)
    if type(book_id_list) == int:
        book_id_list= [book_id_list]
    print(book_id_list)
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    books = ttm_sql.query(Book).filter(Book.id.in_(book_id_list)).all()

    for book in books:
        print(book.id)
        book.delete = 1

    ttm_sql.commit()
    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})