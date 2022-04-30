from sanic import Blueprint
from apps.web_api.view import member

member_bp = Blueprint(name='用户', url_prefix='/member', strict_slashes=True)

member_bp.add_route(member.login, '/login', ['POST'], name='login')  #登录
member_bp.add_route(member.register, '/register', ['POST'], name='register')  #注册
member_bp.add_route(member.logout, '/logout', ['POST'], name='logout')  #退出登录
member_bp.add_route(member.get_detail, '/get_detail', ['POST'], name='get_detail')  # 账号信息
member_bp.add_route(member.up_detail, '/up_detail', ['POST'], name='up_detail')  #修改账号信息
member_bp.add_route(member.up_passwd, '/up_passwd', ['POST'], name='up_passwd')  #修改密码
member_bp.add_route(member.getInfo, '/getInfo', name='getInfo')  #用户信息
