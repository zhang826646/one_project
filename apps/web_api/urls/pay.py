from sanic import Blueprint
from apps.web_api.view import pay

pay_bp = Blueprint(name='支付', url_prefix='/pay', strict_slashes=True)

pay_bp.add_route(pay.goods_list, '/goods_list', name='goods_list')  #
pay_bp.add_route(pay.order_pay, '/order_pay', ['POST'], name='order_pay')  # 开始支付
pay_bp.add_route(pay.alipay_notify, uri='/alipay_notify', methods=['POST'], name='pay_alipay_notify')  # 支付宝异步通知
pay_bp.add_route(pay.pay_book, '/pay_book', ['POST'], name='pay_book')  #注册
# pay_bp.add_route(pay.logout, '/logout', ['POST'], name='logout')  #退出登录
# pay_bp.add_route(pay.get_detail, '/get_detail', ['POST'], name='get_detail')  # 账号信息
# pay_bp.add_route(pay.up_detail, '/up_detail', ['POST'], name='up_detail')  #修改账号信息
# pay_bp.add_route(pay.up_passwd, '/up_passwd', ['POST'], name='up_passwd')  #修改密码
# pay_bp.add_route(pay.getInfo, '/getInfo', name='getInfo')  #用户信息
