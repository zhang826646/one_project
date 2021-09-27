from common.dao.base import BaseModel
from sqlalchemy import Column, Integer, text, String, SmallInteger, TIMESTAMP, DECIMAL, Text, Date
from common.libs.comm import now


class Member(BaseModel):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, default='', comment='昵称')
    nickname = Column(String(255), default='', comment='第三方昵称')
    avatar = Column(String(255), default='', comment='头像')
    email = Column(String(255), default='', comment='邮箱')
    zone = Column(String(50), default='', comment='区号')
    phone = Column(String(50), comment='手机号')
    password = Column(String(50), default='', comment='密码')
    credit = Column(Integer, default=0, comment='积分')
    level = Column(SmallInteger, default=1, comment='等级')
    vip_expire_at = Column(Integer, default=0, comment='vip过期时间')
    created_at = Column(Integer(), default=now, comment='注册时间')
    updated_at = Column(Integer(), default=now, comment='更新时间')






