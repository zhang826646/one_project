from sanic import Blueprint

from .english import english_bp
from .mib import mib_bp
# from .article import article_bp
# from .book import book_bp
# from .pay import pay_bp

mobile_blueprint = Blueprint.group(
    english_bp,
    mib_bp,
    #
    #article_bp,
    # book_bp,
    # pay_bp,
    url_prefix='/mobile',
)