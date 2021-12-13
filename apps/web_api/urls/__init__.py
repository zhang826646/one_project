from sanic import Blueprint

from .member import member_bp
from .group import group_bp


blueprint = Blueprint.group(
    member_bp,
    group_bp,
    url_prefix='/web',
)