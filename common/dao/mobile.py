from common.dao.base import BaseModel
from sqlalchemy import Column, Integer, text, String, SmallInteger, TIMESTAMP, DECIMAL, Text, Date, func


# 专业表
class Specialty(BaseModel):
    __tablename__ = '_mobil_specialty'
    id = Column(Integer, primary_key=True, comment='专业 ID')
    title = Column(String(200), comment='专业昵称')
    brief = Column(String(200), default='', comment='简介')
    quantity = Column(Integer, primary_key=True, comment='课程量')
    delete = Column(Integer, default=0, comment='是否删除：1已删除 0未删除')
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


# 选表
class Course(BaseModel):
    __tablename__ = '_mobile_course'
    id = Column(Integer, primary_key=True, comment='ID')
    member_id = Column(Integer, comment='用户id')
    specialty_id = Column(Integer, primary_key=True, comment='专业id')
    plan = Column(Integer, primary_key=True, comment='计划天数')
    fulfill = Column(Integer, primary_key=True, comment='完成量')
    delete = Column(Integer, default=0, comment='是否删除：1已删除 0未删除')
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')

# word
class EN_word(BaseModel):
    __tablename__ = '_mobile_word'
    id = Column(Integer, primary_key=True, comment='ID')
    specialty_id = Column(Integer, primary_key=True, comment='专业id')
    en_word = Column(String(255), comment='英文')
    zh_word = Column(String(255), default='', comment='中文')
    soundmark = Column(String(255), default='', comment='音标')
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')

#
class Answer(BaseModel):
    __tablename__ = '_mobile_answer'
    id = Column(Integer, primary_key=True, comment='ID')
    specialty_id = Column(Integer, primary_key=True, comment='专业id')
    topic = Column(String(255), comment='问题')
    solution = Column(String(255), default='', comment='答案')
    delete = Column(Integer, default=0, comment='是否删除：1已删除 0未删除')
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')