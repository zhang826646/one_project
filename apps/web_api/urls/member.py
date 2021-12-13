from sanic import Blueprint
from apps.web_api.view import member

member_bp = Blueprint(name='用户', url_prefix='/member', strict_slashes=True)

member_bp.add_route(member.login, '/login', ['POST'], name='login')  #登录
member_bp.add_route(member.register, '/register', ['POST'], name='register')  #注册


member_bp.add_route(member.index, '/index', ['GET'], name='index')  #主页