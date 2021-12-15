from sanic import Blueprint
from apps.web_api.view import group

group_bp = Blueprint(name='社区', url_prefix='/group', strict_slashes=True)

group_bp.add_route(group.index, '/index', ['GET'], name='index')  #主页
group_bp.add_route(group.cat_post, '/cat_post/<post_id:int>', ['GET'], name='group_cat_post')  #文章详情