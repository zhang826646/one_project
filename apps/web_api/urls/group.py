from sanic import Blueprint
from apps.web_api.view import group

group_bp = Blueprint(name='社区', url_prefix='/group', strict_slashes=True)

group_bp.add_route(group.index, '/index', ['GET'], name='index')  #主页