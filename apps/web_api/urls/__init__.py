from sanic import Blueprint

from .member import member_bp


blueprint = Blueprint.group(
    member_bp,

    url_prefix='/web',
)