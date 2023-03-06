from sanic import Blueprint
from apps.mobile_api.view import english

english_bp = Blueprint(name='mobile_单词', url_prefix='/applet', strict_slashes=True)

english_bp.add_route(english.specialty_list, '/specialty_list', ['POST'], name='specialty_list')  # 专业
# english_bp.add_route(english.member_specialty_list, '/member_specialty_list', ['POST'], name='member_specialty_list')  # 已选专业
english_bp.add_route(english.english_word, '/english_word', ['POST'], name='english_word')  # 详情