from sanic import Blueprint
from apps.web_api.view import article

article_bp = Blueprint(name='文章', url_prefix='/article', strict_slashes=True)

article_bp.add_route(article.getArticleList, '/getArticleList', ['POST'], name='getArticleList')  #banner