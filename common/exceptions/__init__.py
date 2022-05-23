class ApiCode(object):
    SUCCESS = 200
    # 系统级别错误
    NORMAL_SYSTEM_ERR = 100001  # 普通系统错误
    UNKNOWN_ERR = 100002  # 未知错误
    PARAM_ERR = 100003  # 参数错误
    SERVER_ERR = 100004  # 服务器错误
    VERSION_LOW = 100006  # 版本过低
    ILLEGAL_REQ = 100007  # 请求非法
    TOO_FREQUENT = 100010  # 请求频繁
    NAMI_API_ERR = 100020  # 纳米OpenAPI错误

    # 业务错误
    NORMAL_ERR = 200000  # 普通业务错误
    NOT_LOGIN = 201000  # 未登录
    NO_PERMISSION = 201001  # 没有权限
    TOKEN_EXPIRED = 201002  # token过期 客户端会踢下线
    ABNORMAL_LOGIN = 201003  # 异常登录
    NOT_AUTHENTICATED = 201005  # 未实名认证
    AUTHENTICATING = 201006  # 实名认证中
    SILENCE = 201007  # 用户被禁言或发言中包含屏蔽字
    EMPTY_RED_PACK = 201008  # 红包被抢完了
    MATCH_NOT_FOUND = 202000  # 没有找到该场比赛
    REPEAT_ERROR = 202001  # 重复操作错误
    SUSPICIOUS = 202002  # 可疑操作,需要验证是否是机器人

    # 弹窗提示
    ALERT_PROMPT = 300000


class Exception(Exception):
    msg = '未知错误'
    code = ApiCode.UNKNOWN_ERR
    data = None

    def __init__(self, code=None, msg=None, data=None):
        self.msg = msg if msg is not None else self.msg
        self.code = code if code is not None else self.code
        self.data = data or self.data
        Exception.__init__(self, self.msg)


class AlertPrompt(Exception):
    def __init__(self, msg='', submit='确认', cancel=None, image=None, submit_extra=None, cancel_extra=None):
        data = {
            'message': msg
        }
        if submit:
            data['submit'] = {
                'text' : submit,
                'extra': submit_extra
            }
        if cancel:
            data['cancel'] = {
                'text' : cancel,
                'extra': cancel_extra
            }
        if image:
            data['image'] = image
        super(AlertPrompt, self).__init__(code=ApiCode.ALERT_PROMPT, msg='', data=data)


class TaskExecuteError(Exception):
    def __init__(self, code=ApiCode.NORMAL_ERR, msg='任务执行出错', data=None, silent=False):
        self.silent = silent
        super(TaskExecuteError, self).__init__(code=code, msg=msg, data=data)


class TaskRepeatError(TaskExecuteError):
    msg = '任务重复执行'
    code = ApiCode.NORMAL_ERR


class InvalidRequestError(Exception):
    msg = '请求非法'
    code = ApiCode.ILLEGAL_REQ
    data = None


class MatchNotFound(Exception):
    msg = '没有找到该场比赛'
    code = ApiCode.MATCH_NOT_FOUND


class TeamNotFound(Exception):
    msg = '没有找到该队伍'
    code = ApiCode.MATCH_NOT_FOUND


class CompetitionNotFound(Exception):
    msg = '没有找到该赛事'
    code = ApiCode.MATCH_NOT_FOUND


class ApiError(Exception):
    """
    自定义 ApiError
    范例：
    from common.exceptions import ApiError
    if not username or not password:
        raise ApiError(code=ApiCode.PARAM_ERR, msg='参数错误')
    """
    code = ApiCode.NORMAL_ERR


class InvalidPwdError(ApiError):
    msg = '密码须包含英文字母、数字、标点符号中至少2种，长度在6-30位'


class InvalidVerifyCodeError(ApiError):
    msg = '验证码不正确'


class NoPermissionError(ApiError):
    msg = '没有权限'
    code = ApiCode.NO_PERMISSION


class NoRealNameAuthError(ApiError):
    msg = '尚未实名认证'
    code = ApiCode.NOT_AUTHENTICATED


class EmptyRedPacketError(ApiError):
    msg = ''
    code = ApiCode.EMPTY_RED_PACK


class NotLoginError(ApiError):
    msg = '请先登录'
    code = ApiCode.NOT_LOGIN


class TokenExpiredError(ApiError):
    msg = '请重新登录'
    code = ApiCode.TOKEN_EXPIRED


class TooFrequentError(ApiError):
    msg = '您的操作过于频繁，请稍候再试'
    code = ApiCode.TOO_FREQUENT


class LoginFrequentError(TooFrequentError):
    msg = '失败次数过多，请稍后再尝试登录'


class BusyError(ApiError):
    msg = '服务忙，请重试'


class SuspiciousError(ApiError):
    msg = '操作需要进行验证'
    code = ApiCode.SUSPICIOUS


class UnknownError(ApiError):
    msg = '未知错误'
    code = ApiCode.UNKNOWN_ERR


class HighRiskError(ApiError):
    msg = '触发天级流控系统，操作被限制'


class InLogoffError(ApiError):
    msg = '此账户正在注销中，操作被限制'


class SportApiError(ApiError):
    msg = '数据API请求错误'
    code = ApiCode.NAMI_API_ERR
    data = {}


class NAMIRateLimitError(SportApiError):
    msg = '纳米API请求频率超过限制'
