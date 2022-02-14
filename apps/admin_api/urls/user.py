from sanic import Blueprint
from apps.admin_api.view import user

user_bp = Blueprint(name='管理员', url_prefix='/user', strict_slashes=True)

user_bp.add_route(user.login, '/login', ['POST'], name='login')  #登录
user_bp.add_route(user.logout, '/logout', ['POST'],name='logout')  #用户登出
user_bp.add_route(user.info, '/info', name='info')  # 用户信息
# user_bp.add_route(user.register, '/register', ['POST'], name='register')  #注册
# user_bp.add_route(user.get_detail, '/get_detail', ['POST'], name='get_detail')  # 账号信息
# user_bp.add_route(user.up_detail, '/up_detail', ['POST'], name='up_detail')  #修改账号信息
# user_bp.add_route(user.up_passwd, '/up_passwd', ['POST'], name='up_passwd')  #修改密码