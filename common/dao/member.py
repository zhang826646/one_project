from common.dao.base import BaseModel
from sqlalchemy import Column, Integer, text, String, SmallInteger, TIMESTAMP, DECIMAL, Text, Date
from common.libs.comm import now


class TtmMember(BaseModel):
    __tablename__ = '_ttm_members'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, default='', comment='昵称')
    avatar = Column(String(255), default='', comment='头像')
    email = Column(String(255), default='', comment='邮箱')
    zone = Column(String(50), default='', comment='区号')
    phone = Column(String(50), comment='手机号')
    password = Column(String(50), default='', comment='密码')
    banned = Column(SmallInteger(), default=0, comment='封禁 [0:正常|1:封禁]')
    credit = Column(Integer, default=0, comment='积分')
    level = Column(SmallInteger, default=1, comment='等级')
    money_nwdbl = Column(DECIMAL(12, 2), default=0, comment='不可提现T币')
    money_wdbl = Column(DECIMAL(12, 2), default=0, comment='可提现T币')
    authenticated = Column(SmallInteger(), default=0, comment='是否是实名认证')
    vip_expire_at = Column(Integer, default=0, comment='vip过期时间')
    created_at = Column(Integer(), default=now, comment='注册时间')
    updated_at = Column(Integer(), default=now, comment='更新时间')
    sex = Column(Integer, default=1, comment='性别 0：女 1:男')
    remark = Column(String(255), default='', comment='简介')






