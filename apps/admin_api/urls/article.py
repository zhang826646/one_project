from sanic import Blueprint
from apps.admin_api.view import article

article_bp = Blueprint(name='admin_文章', url_prefix='/article', strict_slashes=True)

article_bp.add_route(article.article_list, '/article_list', ['POST'], name='article_list')  #文章列表
article_bp.add_route(article.save_article, '/save_article', ['POST'], name='create_article')  #创建文章
article_bp.add_route(article.article_detali, '/article_detali/<article_id:int>', name='article_detali')  #查看文章
article_bp.add_route(article.delete_article, '/delete_article', ['POST'],name='delete_post')  #查看文章
