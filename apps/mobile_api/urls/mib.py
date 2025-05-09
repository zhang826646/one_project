from sanic import Blueprint
from apps.mobile_api.view import mib

mib_bp = Blueprint(name='mib', url_prefix='/mib', strict_slashes=True)


mib_bp.add_route(mib.wechat_msg, '/wechat_msg', ['POST'], name='wechat_msg')  # 详情
mib_bp.add_route(mib.ding_msg, '/ding_msg', ['POST'], name='ding_msg')  # 详情