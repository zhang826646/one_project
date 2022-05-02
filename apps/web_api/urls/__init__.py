from sanic import Blueprint

from .member import member_bp
from .group import group_bp
from .comm import commp_bp
from .article import article_bp
from .pay import pay_bp

web_blueprint = Blueprint.group(
    member_bp,
    group_bp,
    commp_bp,
    article_bp,
    pay_bp,
    url_prefix='/web',
)
