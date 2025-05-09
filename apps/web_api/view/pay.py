from sanic_openapi import doc
from sanic.response import json
# from apps import mako,render_template
from typing import Dict, List, Tuple, Union
from sqlalchemy import and_,or_
from datetime import datetime
import ujson
from common.dao.circle import CirclePost,CircleComment
from common.dao.member import TtmMember
from common.dao.pay import TtmGoods
from common.exceptions import ApiError,ApiCode
from common.libs.aio import run_sqlalchemy
from common.libs.comm import now
from apps.comm.pay import AliPayProxy
from alipay import AliPay
import urllib.parse
from common.libs.tokenize_util import encrypt_web_token,decrypt_web_token
from sanic.response import text
from common.dao.pay import PayRecord
from common.dao.book import Book
import string
import random
import os
from apps.web_api.decorators import authorized

@doc.summary('banner')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def goods_list(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    # product_id = request.valid_data.get('product_id')  # 商品id
    # uid = request.valid_data.get('uid')  # 商品id
    # amount = request.valid_data.get('amount', 1)  # 数量
    # pay_type = request.valid_data.get('pay_type')  # 支付方式 config.apps.pay.PayType
    # yop_pay_type = request.valid_data.get('yop_pay_type')

    @run_sqlalchemy()
    def get_goods(db_session):
        return db_session.query(TtmGoods).filter(TtmGoods.on_sale == 1).all()

    goods = await get_goods(ttm_sql)
    goods_list=[]
    for row in goods:
        item = {
            'id': row.id,
            'name': row.goods_name,
            'sm_logo': row.sm_logo,
            'price': row.price,
            'goods_desc': row.goods_desc,
            'created_at': row.created_at,
        }
        goods_list.append(item)
    return json({
        'code': 0,
        'data': goods_list}
    )


@doc.summary('banner')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def order_pay(request):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    product_id = request.json.get('product_id')  # 商品id
    # uid = request.json.get('uid')  # uid
    amount = request.json.get('amount', 1)  # 数量
    pay_type = request.json.get('pay_type')  # 支付方式 config.apps.pay.PayType
    yop_pay_type = request.json.get('yop_pay_type')
    token = request.cookies.get('Ttm-Token')

    if not token:
        raise ApiError()
    token= urllib.parse.unquote(token)
    user_info = decrypt_web_token(token)
    uid = user_info.get('uid')

    @run_sqlalchemy()
    def get_goods(db_session):
        return db_session.query(TtmGoods).filter(TtmGoods.id==product_id).first()

    goods = await get_goods(ttm_sql)
    if not goods:
        raise ApiError(msg='商品不存在')

    out_trade_no = datetime.now().strftime("%Y%m%d%H%M%S") + ''.join(random.sample(string.digits, 4))  # 生成订单号

    current = now()
    payrecord = PayRecord()
    payrecord.uid = uid
    payrecord.goods_id = goods.id
    payrecord.alipay_order = out_trade_no
    payrecord.count = 1
    payrecord.money = goods.price
    payrecord.status = 0
    payrecord.created_at = current

    ttm_sql.add(payrecord)
    ttm_sql.commit()

    alipay = AliPayProxy('http://123.60.24.197/web/pay/alipay_notify',return_url='http://www.iuttm.cn/blog/member', debug=True)

    order_string = alipay.page_pay(
        subject='TTM购买金币', body=str(goods.t_gold), out_trade_no=out_trade_no, total_amount=str(goods.price))


    # data['transaction_id'] = transaction.id


    return json({
        'code':0,
        'data':{'pay_url': order_string}
    })


"""
支付宝会把参数传递给return_url 返回
http://127.0.0.1:5000/orders.html?
charset=utf-8&   编码
out_trade_no=3&   订单id
method=alipay.trade.wap.pay.return&
total_amount=0.01&   金额
sign=AUOC5QZuyZVwQvPVjocUXyR8h9NkINDy8DEtUti%2BWg8Cd1JYitwJZ%2BMeN2Jo6GfBKnmCCjOTSVJSSnfO%2FKbySmy0tHHLB2T%2FBTLKO1x8w0NeN%2Bvk8U6WPktfOgKgV%2B%2FnEMcQ7LmIvudTAF3mBPggufJ00gZM0y1aFbyvDCu2FTMQxOYaJflFmNRC0i6NIbzTzjYEH3dW5b2qB9r%2Fcqb%2F7AxmVAA%2B61s8w%2FeKS%2BO83JGAiQ8epoPY3daPwYeSaAfe7hYryjip3eoIQQAdM3KxihgRGDH%2BvMUTVz69R6iTSjMcAapia4czBAhPbIZXdbwhT3fbNLf1SKkQxVqxNj37dQ%3D%3D&
trade_no=2020052222001458430500991696&  # 支付宝交易流水号
auth_app_id=2016101700711668&
version=1.0&  
app_id=2016101700711668&
sign_type=RSA2&
seller_id=2088102180059499&
timestamp=2020-05-22+13%3A22%3A28
"""

@doc.summary('banner')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': {'token': doc.String('Token')}
}, content_type='application/json', description='Request True')
async def alipay_notify(request):
    method = request.method
    if method == 'GET':
        request_data = request.args
    else:
        request_data = request.form
    print(request_data)

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    out_trade_no = request_data.get('out_trade_no')
    buyer_pay_amount = request_data.get('buyer_pay_amount')
    print(out_trade_no,buyer_pay_amount)


    payrecord=ttm_sql.query(PayRecord).filter(PayRecord.alipay_order == out_trade_no).first()

    payrecord.status=0
    print(payrecord.id,payrecord.uid)
    goods = ttm_sql.query(TtmGoods).filter(TtmGoods.price == float(buyer_pay_amount)).first()
    print(goods.id)
    member = ttm_sql.query(TtmMember).filter(TtmMember.id == payrecord.uid).first()
    print(member.id)
    member.money_nwdbl = member.money_nwdbl + goods.t_gold

    ttm_sql.commit()


    print('支付宝回调成功')
    return text('success')



@doc.summary('banner')
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
}, content_type='application/json', description='Request True')
async def pay_book(request):
    book_id = request.json.get('book_id')

    token = request.cookies.get('Ttm-Token')
    if not token:
        raise ApiError(code=200 ,msg='请先登录')
    token= urllib.parse.unquote(token)
    user_info = decrypt_web_token(token)
    uid = user_info.get('uid')

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    ttm_redis = await request.app.ttm.get_redis('ttm_redis')
    ttm_redis = await request.app.ttm.get_redis('ttm_redis')
    buy_ids = await ttm_redis.zrange(f'z:buy_book:{uid}')
    if book_id not in buy_ids:
        member = ttm_sql.query(TtmMember).filter(TtmMember.id == uid).first()
        if member.money_nwdbl < 10:
            raise ApiError(msg='金币不足，请先充值金币！')
        member.money_nwdbl -= 10
        ttm_sql.commit()


    book = ttm_sql.query(Book).filter(Book.id == book_id).first()
    item= {
        'book_url':f'http://cdn.iuttem.cn/{book.book_url}',
        'down_url':book.down_url
    }
    await ttm_redis.zadd(f'z:buy_book:{uid}', now(), book.id)

    return json({'code':0,'data':item})


# @doc.summary('获取音乐')
# @doc.produces({
#     'code': doc.Integer('状态码'),
#     'msg' : doc.String('消息提示'),
# }, content_type='application/json', description='Request True')
# async def pay_book(request):
#
#
#
#
#     return json(bannn)