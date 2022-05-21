from sanic import Blueprint
from apps.web_api.view import comm

commp_bp = Blueprint(name='公共', url_prefix='/comm', strict_slashes=True)

commp_bp.add_route(comm.getBannerList, '/getBannerList', ['POST'], name='getBannerList')  #banner
commp_bp.add_route(comm.getPartnerList, '/getPartnerList', name='getPartnerList')  #友情链接
commp_bp.add_route(comm.getTopMusicList, '/getTopMusicList', name='getTopMusicList')  #音乐
commp_bp.add_route(comm.message_list, '/message_list', name='message_list')  # 获取信息
