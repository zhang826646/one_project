from sanic import Blueprint
from apps.web_api.view import article

article_bp = Blueprint(name='文章', url_prefix='/article', strict_slashes=True)

article_bp.add_route(article.getArticleList, '/getArticleList', ['POST'], name='getArticleList')  #文章
article_bp.add_route(article.getTagList, '/getTagList', name='getTagList')  #文章
article_bp.add_route(article.getRecommendArticleList, '/getRecommendArticleList', name='getRecommendArticleList')  #推荐文章
article_bp.add_route(article.getArticleDetail, '/getArticleDetail/<article_id:int>', name='getArticleDetail')  #文章详情
# article_bp.add_route(article.getRelevantArticle, '/getRelevantArticle/<article_id:int>', name='getRelevantArticle')  #相关推荐
article_bp.add_route(article.getArticleComment, '/getArticleComment/<article_id:int>', name='getArticleComment')  #获取评论
article_bp.add_route(article.saveArticle, '/saveArticle', ['POST'], name='saveArticle')  #保存文章
article_bp.add_route(article.addComment, '/addComment', ['POST'], name='addComment')  #保存评论
