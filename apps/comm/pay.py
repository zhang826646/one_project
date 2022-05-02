from config.apps.pay import AliPayApp
from alipay import AliPay


def get_alipay_app(notify_url, app_type='app', debug=False):
    """
    获取AliPay实例
    :param app_type: app|web|wap
    :param notify_url:
    :param debug:
    :return:
    """
    # rand = random.randint(1, 10)
    # 避免风控问题
    # if app_type == 'app':
    #     if rand <= 8:
    #         app_config = AliPayApp4AppAndWebMinor
    #     elif rand <= 9:
    #         app_config = AliPayApp4AppMinor
    #     else:
    #         app_config = AliPayApp4AppAndWebMain
    # elif app_type == 'web':
    #     if rand <= 8:
    #         app_config = AliPayApp4AppAndWebMinor
    #     elif rand <= 9:
    #         app_config = AliPayApp4AppAndWebMain
    #     else:
    #         app_config = AliPayApp4Web
    # elif app_type == 'wap':
    #     app_config = AliPayApp4Web
    # else:
    #     raise ApiError(msg='Invalid app type')
    # if debug:
    #     app_config = AliPayConfigV2
    # else:

    app_config = AliPayApp
    return AliPay(
        appid=app_config.APP_ID,
        app_notify_url=notify_url,  # the default notify path
        app_private_key_string=app_config.APP_PRI_KEY,
        alipay_public_key_string=app_config.ALI_PUB_KEY,
        sign_type=app_config.SIGN_TYPE,  # RSA or RSA2
        debug=debug  # False by default
    )


class AliPayProxy(object):

    def __init__(self, notify_url, return_url=None, debug=False):
        self.debug = debug
        self.notify_url = notify_url
        self.return_url = return_url
        self.app_alipay = get_alipay_app(notify_url, 'app', self.debug)
        self.web_alipay = get_alipay_app(notify_url, 'web', self.debug)
        self.wap_alipay = get_alipay_app(notify_url, 'wap', self.debug)
        self.gateway = 'https://openapi.alipaydev.com/gateway.do'
        # if debug:
        #     self.gateway = 'https://openapi.alipaydev.com/gateway.do'
        # else:
        #     self.gateway = 'https://openapi.alipay.com/gateway.do'

    def app_pay(self, subject, body, out_trade_no, total_amount):
        """
        获取orderstring返回给移动端调起支付宝应用
        :param subject:
        :param body:
        :param out_trade_no:
        :param total_amount:
        :return:
        """
        return self.app_alipay.api_alipay_trade_app_pay(
            subject, out_trade_no, total_amount, self.notify_url, body=body)

    def page_pay(self, subject, body, out_trade_no, total_amount):
        """
        构造web网页支付的URL
        :param subject:
        :param body:
        :param out_trade_no:
        :param total_amount:
        :return:
        """
        print(subject,out_trade_no,total_amount,self.return_url,self.notify_url,body)
        order_string = self.web_alipay.api_alipay_trade_page_pay(
            subject, out_trade_no, total_amount,self.return_url, self.notify_url, body=body)
        return self.gateway + '?' + order_string

    def wap_pay(self, subject, body, out_trade_no, total_amount, return_url=None):
        """
        构造移动端网页支付的URL
        :param subject:
        :param body:
        :param out_trade_no:
        :param total_amount:
        :param return_url:
        :return:
        """
        order_string = self.wap_alipay.api_alipay_trade_wap_pay(
            subject, out_trade_no, total_amount, return_url or self.return_url, self.notify_url, body=body)
        return self.gateway + '?' + order_string

    def verify_sign(self, app_id, data, signature):
        """
        验签
        :param app_id:
        :param data:
        :param signature:
        :return:
        """
        app_config = ALIPAY_APP_MAPPING.get(app_id)
        if not app_config:
            return False
        alipay = AliPay(
            appid=app_config.APP_ID,
            app_notify_url=self.notify_url,
            app_private_key_string=app_config.APP_PRI_KEY,
            alipay_public_key_string=app_config.ALI_PUB_KEY,
            sign_type=app_config.SIGN_TYPE,
            debug=self.debug
        )
        return alipay.verify(data, signature)
