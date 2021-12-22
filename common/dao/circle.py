from common.dao.base import BaseModel
from sqlalchemy import Column, Integer, text, String, SmallInteger, TIMESTAMP, DECIMAL, Text, Date
from common.libs.comm import now


class CirclePost(BaseModel):
    __tablename__ = '_circle_post'

    id = Column(Integer, primary_key=True)
    catalog_id = Column(Integer, comment='板块ID')
    uid = Column(Integer, comment='用户ID')
    type = Column(SmallInteger, default=0, comment='类型[1技术|2生活]')
    title = Column(String(50), default='', comment='帖子标题')
    content = Column(Text(), nullable=True, default='', comment='帖子内容')
    tag = Column(String(50), nullable=True, default='', comment='标签')
    deleted = Column(SmallInteger, default=0, comment='删除[0:正常|1:删除]')
    locked = Column(SmallInteger, default=0, comment='锁定(禁止回复)[0:正常|1:锁定]')
    picked = Column(SmallInteger, default=0, comment='精选[0:正常|1:精选]')
    hidden = Column(SmallInteger, default=0, comment='隐藏[0:正常|1:隐藏]')
    total_comments = Column(SmallInteger, default=0, comment='评论总数')
    total_floors = Column(SmallInteger, default=1, comment='楼层总数')
    total_attachments = Column(SmallInteger, default=0, comment='图片总数')
    attachments = Column(Text(), nullable=True, default='', comment='图片')
    last_replied_at = Column(Integer, default=0, comment='最近回复时间')
    created_at = Column(Integer, default=now, comment='创建时间')


class CircleComment(BaseModel):
    __tablename__ = '_circle_comment'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, comment='帖子ID')
    uid = Column(Integer, comment='用户ID')
    floor = Column(SmallInteger, default=0, comment='第几楼层')
    parent_id = Column(SmallInteger, default=0, comment='父级评论ID')
    content = Column(Text(), nullable=True, default=0, comment='评论内容')
    deleted = Column(SmallInteger, default=0, comment='是否删除[0:正常|1:删除]')
    hidden = Column(SmallInteger, default=0, comment='隐藏[0:正常|1:隐藏]')
    created_at = Column(Integer, default=now, comment='创建时间')
    total_replies = Column(Integer, default=0, comment='子回复数量')
    total_attachments = Column(SmallInteger, default=0, comment='图片数量')
    attachments = Column(Text(), nullable=True, default='', comment='图片')


class CircleCatalog(BaseModel):
    __tablename__ = '_circle_catalog'

    id = Column(Integer, primary_key=True)
    catalog_name = Column(Integer, comment='板块名称')
    uid = Column(Integer, comment='用户ID')
    type = Column(SmallInteger, default=0, comment='类型[1技术|2生活]')
    title = Column(String(50), default='', comment='帖子标题')
    content = Column(Text(), nullable=True, default='', comment='帖子内容')
    tag = Column(String(50), nullable=True, default='', comment='标签')
    deleted = Column(SmallInteger, default=0, comment='删除[0:正常|1:删除]')
    locked = Column(SmallInteger, default=0, comment='锁定(禁止回复)[0:正常|1:锁定]')
    picked = Column(SmallInteger, default=0, comment='精选[0:正常|1:精选]')
    hidden = Column(SmallInteger, default=0, comment='隐藏[0:正常|1:隐藏]')
    total_comments = Column(SmallInteger, default=0, comment='评论总数')
    total_floors = Column(SmallInteger, default=1, comment='楼层总数')
    total_attachments = Column(SmallInteger, default=0, comment='图片总数')
    attachments = Column(Text(), nullable=True, default='', comment='图片')
    last_replied_at = Column(Integer, default=0, comment='最近回复时间')
    created_at = Column(Integer, default=now, comment='创建时间')