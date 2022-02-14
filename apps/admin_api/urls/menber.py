from sanic import Blueprint
from apps.admin_api.view import member

member_bp = Blueprint(name='admin_用户', url_prefix='/member', strict_slashes=True)

member_bp.add_route(member.member_list, '/list', ['POST'], name='member_list')  #登录
# member_bp.add_route(member.logout, '/logout', ['POST'],name='logout')  #用户登出
# member_bp.add_route(member.info, '/info', name='info')  # 用户信息
# user_bp.add_route(user.register, '/register', ['POST'], name='register')  #注册
# user_bp.add_route(user.get_detail, '/get_detail', ['POST'], name='get_detail')  # 账号信息
# user_bp.add_route(user.up_detail, '/up_detail', ['POST'], name='up_detail')  #修改账号信息
