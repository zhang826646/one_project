from sanic import Blueprint

from .member import member_bp
from .group import group_db


blueprint = Blueprint.group(
    member_bp,
    group_db,
    url_prefix='/web',
)