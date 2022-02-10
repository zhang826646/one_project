from sanic import Blueprint

from .member import member_bp
from .group import group_bp

web_blueprint = Blueprint.group(
    member_bp,
    group_bp,
    url_prefix='/web',
)
