from sanic import Blueprint

from .user import user_bp
from .menber import member_bp
from .article import article_bp
from .book import book_bp

admin_blueprint = Blueprint.group(
    user_bp,
    member_bp,
    article_bp,
    book_bp,
    url_prefix='/admin',
)