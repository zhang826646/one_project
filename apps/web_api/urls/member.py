from sanic import Blueprint
from apps.web_api.view import member

member_bp = Blueprint(name='用户', url_prefix='/member', strict_slashes=True)

member_bp.add_route(member.login, '/login', ['GET'], name='login')
