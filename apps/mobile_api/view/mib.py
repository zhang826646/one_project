
import re
import ujson
import random
import time
import lxml.html
import aiohttp
from sanic.exceptions import InvalidUsage
from sanic.response import json
from sanic_openapi import doc
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import aliased
from common.helper import dingtalk_helper
from core.task import TaskManager
# from openai import OpenAI
# from common.exceptions import ApiError, ApiCode
# from common.libs.comm import total_number, now, to_int, inc_count
# from common.libs.aio import run_sqlalchemy
# from common.helper.validator_helper import validate_params, CharField, IntegerField, ListField, DictField
# from common.dao.mobile import Specialty, Course, EN_word ,Answer
# from common.dao.member import TtmMember

api_key = 'sk-0dab1a5b7e4e4bfeb84cf4f048fc13b6'
import os

# 1. 清除所有代理环境变量
os.environ.update({
    'HTTP_PROXY': '',
    'HTTPS_PROXY': '',
    'ALL_PROXY': '',
    'NO_PROXY': 'api.deepseek.com,localhost,127.0.0.1'
})

@doc.summary('wechat 信息')
@doc.consumes()
async def wechat_msg(request):
    print(request.__dict__)

    return json({})


@doc.summary('wechat 信息')
@doc.consumes()
async def ding_msg(request):
    dingtalk_url = request.app.config.get('test_dingtalk_url')
    data = request.json
    print(data)

    # 验证签名
    timestamp = request.headers.get('Timestamp')
    sign = request.headers.get('Sign')

    # 获取消息内容
    content = data.get('text', {}).get('content', '').strip()
    user_name = data.get('senderNick', '').strip()
    content = f'{user_name}:{content}'
    # 这里可以添加你的自动回复逻辑
    if '你好' in content:
        reply = "你好，我是小张！"
    elif '时间' in content:
        reply = f"当前时间是: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    elif '冷静' in content:
        reply = f"这周不宜冷静、冷战. \n周星象动荡，水星逆行未止，火星又与土星相刑，正是诸事易生变数的时节。此时若放任情绪翻涌，贸然行动，恐如逆风执炬，必有灼手之患。\n 一则言语易生误会。水火相位下，脱口而出的话常被曲解，争执如野火蔓延，纵使事后百般弥补，裂痕难消。"
    elif '课表' in content or '课程表' in content:
        reply = f'![screenshot](http://cdn.sittm.cn/dandan/dandan_class_table.jpg)\n'

    else:
        # client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1",http_client=None)
        #
        # response = client.chat.completions.create(
        #     model="deepseek-chat",
        #     messages=[
        #         {"role": "user", "content": content},
        #     ],
        #     max_tokens=1024,
        #     temperature=0.7,
        #     stream=False
        # )
        # reply =response.choices[0].message.content
        await TaskManager.send_task(request.app, 'apps.tasks.dandan.send_deepseek', args=(content,))
        return json({})

    title = '您有新的消息提醒'

    await dingtalk_helper.send_dingtalk(dingtalk_url, title, reply)  # 发送钉钉通知

    return json({})
