from common.libs.comm import total_number, now, to_int, inc_count
from common.dao.circle import CirclePost,CircleComment
from common.dao.member import TtmMember
from common.libs.aio import run_sqlalchemy
import msgpack


async def create_message(app,tpye,uid,content='',comment_id=None):
    """
    创建消息
    :param app:
    :param tpye: 1:系统消息|2:评论消息|3:充值消息
    :param comment_id:
    :return:
    """
    ttm_redis = await app.ttm.get_redis('ttm_redis')
    ttm_sql = app.ttm.get_mysql('ttm_sql')

    @run_sqlalchemy()
    def get_Comment_data(db_session):
        return db_session.query(CircleComment, TtmMember) \
            .join(TtmMember, CircleComment.uid == TtmMember.id) \
            .filter(CircleComment.id == comment_id) \
            .first()
    #
    # data += [x['floor'], msgpack.dumps(x)]
    if tpye == 1 and content:
        content=f'系统消息：{content}'
        await ttm_redis.zadd(f'z:message:{uid}', now(),content)
    elif tpye == 2 and comment_id:
        row = await get_Comment_data(ttm_sql)
        content=f'动态消息：{row.TtmMember.name} 回复了你的{"评论" if row.CircleComment.parent_id else "文章"},点击去查看>>?{row.CircleComment.post_id}'
        await ttm_redis.zadd(f'z:message:{uid}', now(), content)



