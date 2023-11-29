
from common.libs.comm import total_number, now, to_int, inc_count
from common.dao.circle import CirclePost,CircleComment
from common.dao.member import TtmMember
from common.libs.aio import run_sqlalchemy
import msgpack
import re

async def dispose_content(app,content):
    """
    创建消息
    :param app:
    :param content:
    :return:
    """
    src_match = re.search(r'src="([^"]+)"', content)







a=dispose_content()