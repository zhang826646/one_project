from sanic import Sanic, Blueprint
from inspect import isawaitable
from distutils.version import LooseVersion
from sanic.exceptions import SanicException, ServerError
from sanic.log import error_logger
import logging
import random
import ujson
from asyncio import CancelledError
from apps.hooks import StartHook
# from apps.tasks.celery import celery_app
# import functools
from sanic.response import json, HTTPResponse, StreamingHTTPResponse
from common.libs.comm import obj2dict, inc_count, get_ipaddr
from sanic.handlers import ErrorHandler
from sanic.exceptions import NotFound, MethodNotSupported, InvalidUsage
from common.exceptions import LeisuException, ApiCode, InvalidRequestError, LoginFrequentError, TooFrequentError
from sanic.request import Request
# from common.libs.crypto import aes_encrypt, caesar_encrypt
import traceback


logger = logging.getLogger('leisu.root')


IP_RATE_LIMIT_SETTINGS = {}
UID_RATE_LIMIT_SETTINGS = {}
CACHE_CONTROL_SETTINGS = {}
CAESAR_ROUTES = set()

RATE_MODIFIER_MAP = {
    's': lambda n: n,
    'm': lambda n: n * 60.0,
    'h': lambda n: n * 60.0 * 60.0,
}


class CommonErrorHandler(ErrorHandler):
    """
    全局异常处理类
    """
    def default(self, request, exception):
        """
        :param Request request:
        :param exception:
        :return:
        """
        if isinstance(exception, (NotFound, MethodNotSupported)):
            # 404、405异常都返回404
            # return response_format(code=404, data=request.url, http_code=404)
            return response_format(code=404, msg='访问资源不存在，请更新最新版本', http_code=404)
        if isinstance(exception, (InvalidUsage,)):
            return response_format(code=ApiCode.ILLEGAL_REQ, msg='请求体解析错误')
        env = request.app.config.get('env')

        if isinstance(exception, LeisuException):
            if env != 'prod' or isinstance(exception, (InvalidRequestError, LoginFrequentError)):
                logger.warning(traceback.format_exc().split('\n')[-4].strip())
                logger.warning(f'exc: {exception.msg}')
                logger.warning(f'path: [{request.method}] {request.path}')
                logger.warning(f'headers: {dict(request.headers)}')
                logger.warning(f'args: {request.args}')
                logger.warning(f'body: {request.body.decode()}')
            # 自定义异常
            response = {'code': exception.code, 'msg': exception.msg}
            if exception.data:
                response['data'] = exception.data
            return response_format(code=exception.code, data=exception.data, msg=exception.msg)
        else:
            logger.error(f'path: [{request.method}] {request.path}')
            logger.error(f'headers: {dict(request.headers)}')
            logger.error(f'args: {request.args}')
            logger.error(f'body: {request.body.decode()}')
            logger.error(f'exception: {exception}')
            logger.error(f'\n{traceback.format_exc()}')
            # sanic在处理超时的时候不会走中间件 需要在这里释放DB资源
            request.app.leisu.remove_mysql_session()
            if env == 'prod':
                return response_format(code=ApiCode.UNKNOWN_ERR, msg='未知错误', http_code=500)
            # 开发环境下其他异常默认让sanic自身处理
            return super().default(request, exception)
#
#
class BaseRequest(Request):
    def __init__(self, *args, **kwargs):
        super(BaseRequest, self).__init__(*args, **kwargs)
        self.valid_data = {}
#
#
# class CacheBlueprint(Blueprint):
#
#     def add_route(
#         self,
#         handler,
#         uri,
#         methods=frozenset({"GET"}),
#         host=None,
#         strict_slashes=None,
#         version=None,
#         name=None,
#         stream=False,
#         cache_age=None,
#         caesar=False,
#         ip_rate_limit=None,
#         uid_rate_limit=None
#     ):
#         if ip_rate_limit:
#             IP_RATE_LIMIT_SETTINGS[f'{handler.__module__}.{handler.__name__}'] = ip_rate_limit
#         if uid_rate_limit:
#             UID_RATE_LIMIT_SETTINGS[f'{handler.__module__}.{handler.__name__}'] = uid_rate_limit
#         if cache_age:
#             CACHE_CONTROL_SETTINGS[f'{handler.__module__}.{handler.__name__}'] = cache_age
#         if caesar:
#             CAESAR_ROUTES.add(f'{handler.__module__}.{handler.__name__}')
#         return super(CacheBlueprint, self).add_route(
#             handler, uri, methods=methods, host=host, strict_slashes=strict_slashes, version=version, name=name, stream=stream)
#
#
async def before_server_start(_app, _loop):
    logger.info('Sanic APP启动前钩子...')
    _app.min = StartHook(_app, _loop)
    # celery_app.conf.update(_app.config)
    # _app.leisu.celery = celery_app

#
# async def after_server_stop(_app, _loop):
#     logger.info('Sanic APP关闭后钩子...')
#     await _app.leisu.server_stop()
#     _app.leisu.remove_mysql_session()
#
#
# async def response_middleware(request, response):
#     request.app.leisu.remove_mysql_session()


class App(Sanic):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('request_class', BaseRequest)
        kwargs.setdefault('error_handler', CommonErrorHandler())
        super(App, self).__init__(*args, **kwargs)
        # self.register_listener(before_server_start, 'before_server_start')
        # self.register_listener(after_server_stop, 'after_server_stop')
        # self.register_middleware(response_middleware, 'response')

    # async def handle_request(self, request, write_callback, stream_callback):
    #     """Take a request from the HTTP Server and return a response object
    #     to be sent back The HTTP Server only expects a response object, so
    #     exception handling must be done here
    #
    #     :param request: HTTP Request object
    #     :param write_callback: Synchronous response function to be
    #         called with the response as the only argument
    #     :param stream_callback: Coroutine that handles streaming a
    #         StreamingHTTPResponse if produced by the handler.
    #
    #     :return: Nothing
    #     """
    #     # Define `response` var here to remove warnings about
    #     # allocation before assignment below.
    #     response = None
    #     cancelled = False
    #     try:
    #         # -------------------------------------------- #
    #         # Request Middleware
    #         # -------------------------------------------- #
    #         response = await self._run_request_middleware(request)
    #         # No middleware results
    #         if not response:
    #             # -------------------------------------------- #
    #             # Execute Handler
    #             # -------------------------------------------- #
    #
    #             # Fetch handler from router
    #             handler, args, kwargs, uri = self.router.get(request)
    #
    #             request.uri_template = uri
    #             if handler is None:
    #                 raise ServerError(
    #                     (
    #                         "'None' was returned while requesting a "
    #                         "handler from the router"
    #                     )
    #                 )
    #             else:
    #                 if not getattr(handler, "__blueprintname__", False):
    #                     request.endpoint = self._build_endpoint_name(
    #                         handler.__name__
    #                     )
    #                 else:
    #                     request.endpoint = self._build_endpoint_name(
    #                         getattr(handler, "__blueprintname__", ""),
    #                         handler.__name__,
    #                     )
    #
    #             # Run response handler
    #             response = handler(request, *args, **kwargs)
    #             if isawaitable(response):
    #                 response = await response
    #     except CancelledError:
    #         # If response handler times out, the server handles the error
    #         # and cancels the handle_request job.
    #         # In this case, the transport is already closed and we cannot
    #         # issue a response.
    #         response = None
    #         cancelled = True
    #     except Exception as e:
    #         # -------------------------------------------- #
    #         # Response Generation Failed
    #         # -------------------------------------------- #
    #         try:
    #             response = self.error_handler.response(request, e)
    #             if isawaitable(response):
    #                 response = await response
    #         except Exception as e:
    #             if isinstance(e, SanicException):
    #                 response = self.error_handler.default(
    #                     request=request, exception=e
    #                 )
    #             elif self.debug:
    #                 response = HTTPResponse(
    #                     "Error while handling error: {}\nStack: {}".format(
    #                         e, traceback.format_exc()
    #                     ),
    #                     status=500,
    #                 )
    #             else:
    #                 response = HTTPResponse(
    #                     "An error occurred while handling an error", status=500
    #                 )
    #     finally:
    #         # -------------------------------------------- #
    #         # Response Middleware
    #         # -------------------------------------------- #
    #         # Don't run response middleware if response is None
    #         # HACK remove db session
    #         request.app.leisu.remove_mysql_session()
    #         if response is not None:
    #             try:
    #                 response = await self._run_response_middleware(
    #                     request, response
    #                 )
    #             except CancelledError:
    #                 # Response middleware can timeout too, as above.
    #                 response = None
    #                 cancelled = True
    #             except BaseException:
    #                 error_logger.exception(
    #                     "Exception occurred in one of response "
    #                     "middleware handlers"
    #                 )
    #         if cancelled:
    #             raise CancelledError()
    #     # pass the response to the correct callback
    #     if write_callback is None or isinstance(
    #             response, StreamingHTTPResponse
    #     ):
    #
    #         if stream_callback:
    #             await stream_callback(response)
    #     else:
    #         write_callback(response)

#
def response_format(code=0, data=None, msg="", http_code=200, headers=None, aes_key=None, caesar=None):
    if data is None:
        data = data
    elif isinstance(data, (str, int, float, list, dict, tuple)):
        data = data
    else:
        data = obj2dict(data)
    if aes_key and caesar:
        raise ValueError('caesar and aes can not be set both.')
    if data:
        if aes_key:
            code = 1  # 1表示使用了AES加密
            # data = aes_encrypt(ujson.dumps(data, ensure_ascii=False), aes_key)
        if caesar:
            offset = random.randint(5, 20)
            code = 100 + offset
            # data = caesar_encrypt(ujson.dumps(data, ensure_ascii=False), offset=offset)
    result = {'code': code, 'data': None, 'msg': msg}
    if code == ApiCode.ALERT_PROMPT:
        # APP弹窗
        result['alert'] = data
    else:
        result['data'] = data
    if headers:
        if 'Cache-Control' in headers:
            try:
                result['age'] = int(headers['Cache-Control'].split('=')[1])
            except (KeyError, ValueError, IndexError):
                logger.warning(traceback.format_exc())
    return json(result, ensure_ascii=False,  status=http_code, headers=headers)
#
#
# def formatter(headers=None, aes=False, env_exclude=('dev', 'local'), caesar=False, hack_version=None):
#     """
#     格式化响应，返回给前端{"msg": msg, "data": data, "code": code}格式
#     :param dict headers: 自定义的请求头
#     :param bool aes: 是否对data字段使用AES加密
#     :param tuple env_exclude: 不在指定环境下加密
#     :param bool caesar: 是否凯撒加密+Gzip
#     :param str hack_version: 针对404的兼容flag
#     :return:
#     """
#     headers = headers or {}
#     env_exclude = env_exclude or ()
#
#     def decorator(method):
#         @functools.wraps(method)
#         async def wrapper(request: BaseRequest, *args, **kwargs):
#             aes_key = None
#             code = 0
#             if aes and request.app.config.env not in env_exclude:
#                 aes_key = request.app.config.aes_key
#             _caesar = caesar and (request.app.config.env not in env_exclude)
#             settings_key = f'{method.__module__}.{method.__name__}'
#             if settings_key in CACHE_CONTROL_SETTINGS:
#                 headers['Cache-Control'] = f'max-age={CACHE_CONTROL_SETTINGS[settings_key]}'
#             try:
#                 if request.method == 'POST':
#                     ip_rate_limit = IP_RATE_LIMIT_SETTINGS.get(settings_key) or request.app.config.IP_RATE_LIMIT
#                     uid_rate_limit = UID_RATE_LIMIT_SETTINGS.get(settings_key) or request.app.config.UID_RATE_LIMTI
#                     # 根据ip限制请求频率
#                     if ip_rate_limit:
#                         ip = get_ipaddr(request)
#                         parts = ip_rate_limit.split('/')
#                         count = int(parts[0])
#                         # 单位转换成秒
#                         seconds = RATE_MODIFIER_MAP[parts[1][-1]](int(parts[1][:-1] or 1))
#                         if await inc_count(
#                                 request.app, f'api:rate_limit:{request.path}:ip:{ip}', ttl=seconds, reset_ttl=False) > count:
#                             raise TooFrequentError()
#                     # 根据uid限制请求频率
#                     if uid_rate_limit:
#                         uid = request['uid'] if 'uid' in request else 0
#                         if uid:
#                             parts = uid_rate_limit.split('/')
#                             count = int(parts[0])
#                             seconds = RATE_MODIFIER_MAP[parts[1][-1]](int(parts[1][:-1] or 1))
#                             if await inc_count(
#                                     request.app, f'api:rate_limit:{request.path}:uid:{uid}', ttl=seconds, reset_ttl=False) > count:
#                                 raise TooFrequentError()
#
#                 data = await method(request, *args, **kwargs)
#                 if isinstance(data, HTTPResponse):
#                     if data.content_type == 'application/json':
#                         if 'Cache-Control' not in data.headers and settings_key in CACHE_CONTROL_SETTINGS:
#                             data.headers['Cache-Control'] = f'max-age={CACHE_CONTROL_SETTINGS[settings_key]}'
#                         try:
#                             _response = ujson.loads(data.body.decode())
#                         except ValueError:
#                             return data
#                         _data = _response['data'] if data.body else None
#                         if request.method == 'GET' and not _data and LooseVersion(request.headers.get('ver')) > LooseVersion(hack_version):
#                             code = 404
#                         return response_format(
#                             code=code,
#                             data=_data,
#                             headers=data.headers,
#                             aes_key=aes_key,
#                             caesar=_caesar
#                         )
#                     else:
#                         return data
#             except Exception as e:
#                 # NOTE 不要在这里处理异常 异常处理全部交给CommonErrorHandler处理
#                 raise
#             if request.method == 'GET' and not data and LooseVersion(request.headers.get('ver')) > LooseVersion(hack_version):
#                 code = 404
#             return response_format(code=code, data=data, headers=headers, aes_key=aes_key, caesar=_caesar)
#         return wrapper
#     return decorator
