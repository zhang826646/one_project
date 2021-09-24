from sanic import Blueprint
from sanic.response import json
from sanic_openapi import doc
from datetime import datetime

# from common.helper.validator_helper import validate_params, IntegerField
# from common.libs.comm import get_ipaddr
# from common.libs.crypto import caesar_encrypt
# from apps.base import formatter, CACHE_CONTROL_SETTINGS

base_bp = Blueprint(name='default', url_prefix='/', strict_slashes=True)


@doc.summary('APP 所有状态接口')
@base_bp.route('/status', strict_slashes=True)
async def app_status(request):
    return json({
        # 'app_config': request.app.config,
        'app_leisu' : request.app.leisu.status()
        # 'app_router': request.app.router.routes_all,
    })


@doc.summary('APP Debug')
@base_bp.route('/debug', strict_slashes=True)
async def app_debug(request):
    return json({
        'cache'          : CACHE_CONTROL_SETTINGS,
        'method'         : request.method,
        'url'            : request.url,
        'query_string'   : request.query_string,
        'query_args'     : request.query_args,
        'form'           : request.form,
        'body'           : request.body,
        # 'ip'             : get_ipaddr(request),
        'request.ip'     : request.ip,
        'X-Real-Ip'      : request.headers.get('X-Real-Ip'),
        'X-Forwarded-For': request.headers.get('X-Forwarded-For'),
        'uri_template'   : request.uri_template,
        'endpoint'       : request.endpoint,
        'headers'        : dict([(k, v) for k, v in request.headers.items()]),
        'cookies'        : request.cookies,
    }, status=200, headers={'X-Served-By': 'LeiSu'})


@doc.summary('HTTP测试接口')
@doc.consumes({
    'status': doc.String('需要返回的http状态码'),
})
@base_bp.route('/httpcode', strict_slashes=True)
# @validate_params(
#     IntegerField(name='status')
# )
async def app_httpcode(request):
    status = request.valid_data.get('status')
    return json({'code': status, 'data': '', 'msg': '错误提示'}, status)


@doc.summary('API AES加密测试')
@doc.consumes(
    doc.JsonBody({
        'data': doc.String('需要测试的加密json格式数据'),
    }), content_type='application/json', location='body', required=False
)
@doc.produces({
    'code': doc.Integer('状态码'),
    'msg' : doc.String('消息提示'),
    'data': doc.String('返回数据'),
})
@base_bp.route('/aes', methods=['POST'], strict_slashes=True)
# @formatter(aes=True)
async def aes(request):
    data = request.json.get('data')
    if data:
        return data
    else:
        return {
            'aoo': 'test中文',
            'boo': 1,
            'coo': [1, 2, 3],
            'url': request.url,
            'now': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

#
# @doc.summary('API凯撒加密测试')
# @doc.consumes()
# @doc.produces({
#     'code': doc.Integer('状态码'),
#     'msg' : doc.String('消息提示'),
#     'data': doc.String('返回数据'),
# })
# @base_bp.route('/caesar', methods=['GET'], strict_slashes=True)
# async def caesar(request):
#     data = caesar_encrypt({
#         'aoo': 'test中文',
#         'boo': 1,
#         'coo': [1, 2, 3],
#         'url': request.url,
#         'now': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     })
#     return json({'code': 106, 'data': data, 'msg': ''})


@doc.summary('健康检查')
@base_bp.route('/check_health', strict_slashes=True)
async def check_health(request):
    return json(await request.app.leisu.check_health())
