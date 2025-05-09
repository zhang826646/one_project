from common.dao.base import BaseModel
from sqlalchemy import Column, Integer, text, String, SmallInteger, TIMESTAMP, DECIMAL, Text, Date, func



# 管理后台用户表
class User(BaseModel):
    __tablename__ = '_admin_user'
    id = Column(Integer, primary_key=True, comment='用户 ID')
    name = Column(String(200), comment='用户昵称')
    email = Column(String(200), default='', comment='邮箱')
    password = Column(String(200), default='', comment='密码')
    real_name = Column(String(20), comment='姓名')
    status = Column(SmallInteger, default=1, comment='状态 [1:正常|0:不存在]')
    banned = Column(SmallInteger, default=0, comment='禁用 [0:否|1:是]')
    group_id = Column(SmallInteger, default=0, comment='用户组 ID')
    last_login = Column(Integer, default=0, comment='上次登录时间')

    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')

