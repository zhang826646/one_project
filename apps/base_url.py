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

@doc.summary('测试')
@base_bp.route('/test', strict_slashes=True)
async def test(request):
    # from apps.tasks.ok import time_up
    # from apps.tasks.ok_sjz import time_up as time_sjz
    # await time_up()
    # await time_sjz()
    from core.task import TaskManager
    # await request.app.celery.send_task('apps.tasks.ok.update_execl', args=())
    # await request.app.celery.send_task('apps.tasks.ok.buil_billiards_list', args=())
    # await request.app.celery.send_task('apps.tasks.ok_sjz.buil_billiards_list', args=())
    # await request.app.celery.send_task('apps.tasks.ok_sjz.w_billiards_list', args=())
    # request.app.ttm.celery.send_task('apps.tasks.ok.time_up', args=())
    # await request.app.celery.send_task('apps.tasks.word.word_updata', args=())
    # print(request.app.ttm.celery)
    # print(request.app.celery)
    # from common.helper import dingtalk_helper
    # dingtalk_url = request.app.config.get('test_dingtalk_url')
    # await TaskManager.send_task(request.app, 'apps.tasks.dandan.send_deepseek', args=('申丹丹:你知道我是谁吗',))
    # await TaskManager.send_task(request.app, 'apps.tasks.dandan.send_deepseek', args=('你嗯什么嗯,嗯能解决问题吗',))
    title = '小张来啦!'
    ttm_redis = await request.app.ttm.get_redis('ttm_redis')
    import msgpack

    content='累'
    reply='小张：丹丹，听起来你今天很疲惫呢。要不要先喝杯温水休息一下？有时候身体累了，心情也会受影响。等你想聊聊的时候，我随时在这里。谭民看到丹丹这么累，也可以温柔地问问\"今天工作很辛苦吗？需要我帮你按按肩膀吗？\"这样的小关心会让对方感觉很温暖哦。'
    print(msgpack.packb([{"role": "user", "content": content}, {"role": "assistant", "content": reply}],
                                       use_bin_type=True))
    await ttm_redis.zadd('z:deepseek:chat_all', now(),
                         msgpack.packb([{"role": "user", "content": content}, {"role": "assistant", "content": reply}],
                                       use_bin_type=True))

    # await dingtalk_helper.send_dingtalk(dingtalk_url, title, '就不散!')  # 发送钉钉通知
    # from apps.tasks.dandan import send_deepseek
    #
    # await send_deepseek('看到了吧, 申丹丹不喜欢你')
    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})

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