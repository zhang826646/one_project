from sanic import Blueprint
from apps.web_api.view import member

member_bp = Blueprint(name='03 用户 V1', url_prefix='/member', version=1, strict_slashes=True)
