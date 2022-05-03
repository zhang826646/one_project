from common.dao.base import BaseModel
from sqlalchemy import Column, Integer, text, String, SmallInteger, TIMESTAMP, DECIMAL, Text, Date, func



# 图书
class Book(BaseModel):
    __tablename__ = '_book'
    id = Column(Integer, primary_key=True, comment='ID')
    title = Column(String(200), comment='书名')
    author = Column(String(200), default='', comment='作者')
    publish = Column(String(200), default='', comment='出版人')
    booktpye = Column(String(20), comment='书籍类型')
    pages = Column(Integer, default=1, comment='总书页')
    book_url = Column(String(200), default='', comment='图书链接')
    cover = Column(String(200), default='', comment='图书封面')
    update_time = Column(Integer, default=0, comment='创建时间')

    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), comment='创建时间')
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')

