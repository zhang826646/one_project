from common.dao.base import BaseModel
from sqlalchemy import Column, Integer, text, String, SmallInteger, TIMESTAMP, DECIMAL, Text, Date
from common.libs.comm import now

# 商品
class TtmGoods(BaseModel):
    __tablename__ = '_ttm_goods'

    id = Column(Integer, primary_key=True)
    goods_name = Column(String(255), nullable=False, default='', comment='商品名称')
    sm_logo = Column(String(255), default='', comment='商品缩略图')
    price = Column(DECIMAL(12, 2), default=0, comment='商品价格')
    t_gold = Column(Integer, default=0, comment='T币金额')
    goods_desc = Column(String(50), default='', comment='商品描述')
    on_sale = Column(Integer, default=1,comment='是否上架：1上架 0下架')
    delete = Column(Integer, default=0, comment='是否删除：1已删除 0未删除')
    created_at = Column(Integer(), default=now, comment='添加时间')

# 充值记录
class PayRecord(BaseModel):
    __tablename__ = '_pay_record'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, default=0,comment='用户ID')
    alipay_order = Column(String(255), default=0, comment='订单ID')
    goods_id = Column(Integer, default=0, comment='商品id')
    count = Column(Integer, default=0, comment='交易数量')
    money = Column(DECIMAL(12, 2), default=0, comment='交易金额')
    status = Column(Integer, default=0, comment='交易状态 0正常1失败')
    created_at = Column(Integer(), default=now, comment='交易时间')




