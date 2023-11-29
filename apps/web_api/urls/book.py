from sanic import Blueprint
from apps.web_api.view import book

book_bp = Blueprint(name='书籍1', url_prefix='/book', strict_slashes=True)

book_bp.add_route(book.book_list, '/book_list',['POST'], name='book_list')  #
book_bp.add_route(book.is_buybook, '/is_buybook/<bid:int>', name='is_buybook')  #
# book_bp.add_route(book.order_pay, '/order_pay', ['POST'], name='order_pay')  # 开始支付
# book_bp.add_route(book.alipay_notify, uri='/alipay_notify', methods=['POST'], name='pay_alipay_notify')  # 支付宝异步通知
# pay_bp.add_route(pay.register, '/register', ['POST'], name='register')  #注册
# pay_bp.add_route(pay.logout, '/logout', ['POST'], name='logout')  #退出登录
# pay_bp.add_route(pay.get_detail, '/get_detail', ['POST'], name='get_detail')  # 账号信息
# pay_bp.add_route(pay.up_detail, '/up_detail', ['POST'], name='up_detail')  #修改账号信息
# pay_bp.add_route(pay.up_passwd, '/up_passwd', ['POST'], name='up_passwd')  #修改密码
# pay_bp.add_route(pay.getInfo, '/getInfo', name='getInfo')  #用户信息
