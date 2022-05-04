from sanic import Blueprint
from apps.admin_api.view import pay

pay_bp = Blueprint(name='交易', url_prefix='/pay', strict_slashes=True)

pay_bp.add_route(pay.record_list, '/record_list', ['POST'], name='record_list')  # 交易列表
pay_bp.add_route(pay.goods_list, '/goods_list', ['POST'], name='goods_list')  # 商品列表
pay_bp.add_route(pay.save_goods, '/save_goods', ['POST'], name='save_goods')  # 商品列表
pay_bp.add_route(pay.pay_goods, '/pay_goods', ['POST'], name='pay_goods')  # 手动发金币
# pay_bp.add_route(pay.book_detali, '/book_detali/<id:int>', name='book_detali')  #查看文章
# pay_bp.add_route(pay.delete_book, '/delete_book', ['POST'],name='delete_book')  #查看文章


