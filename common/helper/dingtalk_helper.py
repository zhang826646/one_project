import time

import aiohttp
from common.exceptions import ApiCode, ApiError
import msgpack
import logging
from core.task import TaskManager
logger = logging.getLogger('ttm.root')
api_key = 'sk-0dab1a5b7e4e4bfeb84cf4f048fc13b6'

async def send_dingtalk(dingtalk_api, title, text, at_phone=None, btns=None):
    headers = {
        'Content-Type' : 'application/json',
        'User-Agent'   : 'python/pyzabbix',
        'Cache-Control': 'no-cache'
    }
    data = {
        'actionCard': {
            'title'         : title,
            'text'          : text,
            'hideAvatar'    : '0',
            'btnOrientation': '0'
        },
        'msgtype': 'actionCard'
    }
    if at_phone:
        data['at'] = {'atMobiles': [at_phone]}
    if btns:
        # data['actionCard'].update({'btns':btns})
        data['actionCard'].update(btns)
    async with aiohttp.ClientSession() as session:
        async with session.post(dingtalk_api, headers=headers, json=data, timeout=10) as response:
            return await response.json()


async def send_deepseek(app,content):
    ttm_redis = await app.ttm.get_redis('ttm_redis')
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    await ttm_redis.zadd('z:deepseek:chat', time.time(), msgpack.packb({"role": "user", "content": content}, use_bin_type=True))
    data = {
        "model": "deepseek-chat",
        "messages": [
                    # {"role": "user", "content": "你是谁?"},
                    # {"role": "assistant", "content": "我是小张,是你的虚拟男友哦,哈哈哈."},
                    {"role": "user", "content": "我是申丹丹"},
                    {"role": "assistant", "content": "你好,申丹丹, 我会照顾好你的"},
                    {"role": "user", "content": content}]
    }


    # response = requests.post(
    #     "https://api.deepseek.com/v1/chat/completions",
    #     headers=headers,
    #     json=data,
    #     proxies={"http": None, "https": None}  # 强制禁用代理
    # )
    # return response.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=120,
                                    proxy=None) as response:
                logger.info(response.status)
                logger.info(response)
                response = await response.json()
        logger.info(response)

        reply = response["choices"][0]["message"]["content"]
    except:
        await TaskManager.send_task(app, 'apps.tasks.dandan.send_deepseek', args=(content,))
        reply = '连接超时, 请联系小张同学处理.'
    return reply