from sanic import Blueprint

from .user import user_bp


admin_blueprint = Blueprint.group(
    user_bp,
    url_prefix='/admin',
)