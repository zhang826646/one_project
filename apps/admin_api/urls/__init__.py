from sanic import Blueprint

from .user import user_bp
from .menber import member_bp

admin_blueprint = Blueprint.group(
    user_bp,
    member_bp,
    url_prefix='/admin',
)