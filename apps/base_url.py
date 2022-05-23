from sanic import Blueprint
from sanic.response import json
from sanic_openapi import doc
from datetime import datetime
from common.libs.comm import now, total_number, to_strtime ,to_str
from common.helper.qiniu_helper import get_upload_token
from common.exceptions import ApiError,ApiCode

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
        'app_config': {'qwe':"qqqqqqqq"},
        # 'app_router': request.app.router.routes_all,
    })



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
            'urls': request.url,
            'now': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }



@doc.summary('七牛云上传token')
@base_bp.route('/con/qiniu_access_token', strict_slashes=True,methods=['POST'])
async def qiniu_access_token(request):
    try:
        img_dir = to_str(request.json.get('img_dir'), 'upload')
    except :
        raise ApiError(code=ApiCode.PARAM_ERR, msg='参数错误')
    if img_dir in ('apk',):
        # 上传apk保持原文件名
        rename = False
    else:
        rename = True
    token = await get_upload_token(img_dir, rename, size=1000)

    data = {
        'code': ApiCode.SUCCESS,
        'data': {
            'token': token
        },
    }
    return json(data)



@doc.summary('admin router')
@base_bp.route('/con/getRouters', strict_slashes=True)
async def app_status(request):

    router_list = [
        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "/system",
            "component": "Layout",
            "children": [
                {
                    "name": "User",
                    "path": "user",
                    "hidden": False,
                    "component": "system/user/index",
                    "meta": {
                        "title": "用户管理",
                        "icon": "user",
                        "noCache": False,
                        "link": None
                    }
                },
            ]
        },

        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "/system",
            "component": "Layout",
            "children": [
                {
                    "name": "Role",
                    "path": "role",
                    "hidden": False,
                    "component": "system/role/index",
                    "meta": {
                        "title": "商品管理",
                        "icon": "peoples",
                        "noCache": False,
                        "link": None
                    }
                }
            ]
        },
        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "/system",
            "component": "Layout",
            "children": [
                {
                    "name": "Dept",
                    "path": "dept",
                    "hidden": False,
                    "component": "system/dept/index",
                    "meta": {
                        "title": "评论管理",
                        "icon": "tree",
                        "noCache": False,
                        "link": None
                    }
                },
            ]
        },
        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "/system",
            "component": "Layout",
            "children": [
                {
                    "name": "Post",
                    "path": "post",
                    "hidden": False,
                    "component": "system/post/index",
                    "meta": {
                        "title": "文章管理",
                        "icon": "post",
                        "noCache": False,
                        "link": None
                    }
                },
            ]
        },
        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "/system",
            "component": "Layout",
            "children": [
                {
                    "name": "Dict",
                    "path": "dict",
                    "hidden": False,
                    "component": "system/dict/index",
                    "meta": {
                        "title": "书籍管理",
                        "icon": "dict",
                        "noCache": False,
                        "link": None
                    }
                },
            ]
        },
        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "/system",
            "component": "Layout",
            "children": [
                {
                    "name": "Config",
                    "path": "config",
                    "hidden": False,
                    "component": "system/config/index",
                    "meta": {
                        "title": "充值记录",
                        "icon": "edit",
                        "noCache": False,
                        "link": None
                    }
                },
            ]
        },
        {
            "name": "System",
            "path": "/system",
            "hidden": False,
            "redirect": "/system",
            "component": "Layout",
            "children": [
                {
                    "name": "Notice",
                    "path": "notice",
                    "hidden": False,
                    "component": "system/notice/index",
                    "meta": {
                        "title": "通知公告",
                        "icon": "message",
                        "noCache": False,
                        "link": None
                    }
                },
            ]
        },
        {
            "name": "Log",
            "path": "log",
            "hidden": False,
            "redirect": "noRedirect",
            "component": "ParentView",
            "alwaysShow": True,
            "meta": {
                "title": "日志管理",
                "icon": "log",
                "noCache": False,
                "link": None
            },
            "children": [
                {
                    "name": "Operlog",
                    "path": "operlog",
                    "hidden": False,
                    "component": "monitor/operlog/index",
                    "meta": {
                        "title": "操作日志",
                        "icon": "form",
                        "noCache": False,
                        "link": None
                    }
                },
                {
                    "name": "Logininfor",
                    "path": "logininfor",
                    "hidden": False,
                    "component": "monitor/logininfor/index",
                    "meta": {
                        "title": "登录日志",
                        "icon": "logininfor",
                        "noCache": False,
                        "link": None
                    }
                }
            ]
        }
    ]
    return json({ "msg": "操作成功", "code": 200,"data": router_list})





    #     {
    #         "msg": "操作成功",
    #         "code": 200,
    #         "data": [
    #             {
    #                 "name": "System",
    #                 "path": "/system",
    #                 "hidden": False,
    #                 "redirect": "noRedirect",
    #                 "component": "Layout",
    #                 "alwaysShow": True,
    #                 "meta": {
    #                     "title": "系统管理",
    #                     "icon": "system",
    #                     "noCache": False,
    #                     "link": None
    #                 },
    #                 "children": [
    #                     {
    #                         "name": "User",
    #                         "path": "user",
    #                         "hidden": False,
    #                         "component": "system/user/index",
    #                         "meta": {
    #                             "title": "用户管理",
    #                             "icon": "user",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Role",
    #                         "path": "role",
    #                         "hidden": False,
    #                         "component": "system/role/index",
    #                         "meta": {
    #                             "title": "商品管理",
    #                             "icon": "peoples",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     # {
    #                     #     "name": "Menu",
    #                     #     "path": "menu",
    #                     #     "hidden": False,
    #                     #     "component": "system/menu/index",
    #                     #     "meta": {
    #                     #         "title": "菜单管理",
    #                     #         "icon": "tree-table",
    #                     #         "noCache": False,
    #                     #         "link": None
    #                     #     }
    #                     # },
    #                     {
    #                         "name": "Dept",
    #                         "path": "dept",
    #                         "hidden": False,
    #                         "component": "system/dept/index",
    #                         "meta": {
    #                             "title": "评论管理",
    #                             "icon": "tree",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Post",
    #                         "path": "post",
    #                         "hidden": False,
    #                         "component": "system/post/index",
    #                         "meta": {
    #                             "title": "文章管理",
    #                             "icon": "post",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Dict",
    #                         "path": "dict",
    #                         "hidden": False,
    #                         "component": "system/dict/index",
    #                         "meta": {
    #                             "title": "书籍管理",
    #                             "icon": "dict",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Config",
    #                         "path": "config",
    #                         "hidden": False,
    #                         "component": "system/config/index",
    #                         "meta": {
    #                             "title": "充值记录",
    #                             "icon": "edit",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Notice",
    #                         "path": "notice",
    #                         "hidden": False,
    #                         "component": "system/notice/index",
    #                         "meta": {
    #                             "title": "通知公告",
    #                             "icon": "message",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Log",
    #                         "path": "log",
    #                         "hidden": False,
    #                         "redirect": "noRedirect",
    #                         "component": "ParentView",
    #                         "alwaysShow": True,
    #                         "meta": {
    #                             "title": "日志管理",
    #                             "icon": "log",
    #                             "noCache": False,
    #                             "link": None
    #                         },
    #                         "children": [
    #                             {
    #                                 "name": "Operlog",
    #                                 "path": "operlog",
    #                                 "hidden": False,
    #                                 "component": "monitor/operlog/index",
    #                                 "meta": {
    #                                     "title": "操作日志",
    #                                     "icon": "form",
    #                                     "noCache": False,
    #                                     "link": None
    #                                 }
    #                             },
    #                             {
    #                                 "name": "Logininfor",
    #                                 "path": "logininfor",
    #                                 "hidden": False,
    #                                 "component": "monitor/logininfor/index",
    #                                 "meta": {
    #                                     "title": "登录日志",
    #                                     "icon": "logininfor",
    #                                     "noCache": False,
    #                                     "link": None
    #                                 }
    #                             }
    #                         ]
    #                     }
    #                 ]
    #             },
    #             {
    #                 "name": "Monitor",
    #                 "path": "/monitor",
    #                 "hidden": False,
    #                 "redirect": "noRedirect",
    #                 "component": "Layout",
    #                 "alwaysShow": True,
    #                 "meta": {
    #                     "title": "系统监控",
    #                     "icon": "monitor",
    #                     "noCache": False,
    #                     "link": None
    #                 },
    #                 "children": [
    #                     {
    #                         "name": "Online",
    #                         "path": "online",
    #                         "hidden": False,
    #                         "component": "monitor/online/index",
    #                         "meta": {
    #                             "title": "在线用户",
    #                             "icon": "online",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Job",
    #                         "path": "job",
    #                         "hidden": False,
    #                         "component": "monitor/job/index",
    #                         "meta": {
    #                             "title": "定时任务",
    #                             "icon": "job",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Druid",
    #                         "path": "druid",
    #                         "hidden": False,
    #                         "component": "monitor/druid/index",
    #                         "meta": {
    #                             "title": "数据监控",
    #                             "icon": "druid",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Server",
    #                         "path": "server",
    #                         "hidden": False,
    #                         "component": "monitor/server/index",
    #                         "meta": {
    #                             "title": "服务监控",
    #                             "icon": "server",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Cache",
    #                         "path": "cache",
    #                         "hidden": False,
    #                         "component": "monitor/cache/index",
    #                         "meta": {
    #                             "title": "缓存监控",
    #                             "icon": "redis",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     }
    #                 ]
    #             },
    #             {
    #                 "name": "Tool",
    #                 "path": "/tool",
    #                 "hidden": False,
    #                 "redirect": "noRedirect",
    #                 "component": "Layout",
    #                 "alwaysShow": True,
    #                 "meta": {
    #                     "title": "系统工具",
    #                     "icon": "tool",
    #                     "noCache": False,
    #                     "link": None
    #                 },
    #                 "children": [
    #                     {
    #                         "name": "Build",
    #                         "path": "build",
    #                         "hidden": False,
    #                         "component": "tool/build/index",
    #                         "meta": {
    #                             "title": "表单构建",
    #                             "icon": "build",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Gen",
    #                         "path": "gen",
    #                         "hidden": False,
    #                         "component": "tool/gen/index",
    #                         "meta": {
    #                             "title": "代码生成",
    #                             "icon": "code",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     },
    #                     {
    #                         "name": "Swagger",
    #                         "path": "swagger",
    #                         "hidden": False,
    #                         "component": "tool/swagger/index",
    #                         "meta": {
    #                             "title": "系统接口",
    #                             "icon": "swagger",
    #                             "noCache": False,
    #                             "link": None
    #                         }
    #                     }
    #                 ]
    #             },
    #             # {
    #             #     "name": "Http://ruoyi.vip",
    #             #     "path": "http://ruoyi.vip",
    #             #     "hidden": False,
    #             #     "component": "Layout",
    #             #     "meta": {
    #             #         "title": "若依官网",
    #             #         "icon": "guide",
    #             #         "noCache": False,
    #             #         "link": "http://ruoyi.vip"
    #             #     }
    #             # }
    #         ]
    #     }
    # )