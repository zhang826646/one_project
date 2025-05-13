from datetime import datetime, timedelta
import chinese_calendar as calendar
import time

from apps.tasks.celery import MyCelery,celery_app, BaseTask
import os
import re
from common.libs.comm import now
import random
import msgpack
import aiohttp
from common.helper import dingtalk_helper
import logging
logger = logging.getLogger('ttm.root')
# 获取当前日期和时间

# 检查某天是否是节假日
# date = now_time.date()
# is_holiday = calendar.is_holiday(date)
# print(f"{date} 是节假日吗？{is_holiday}")
# is_workday = calendar.is_workday(date)
# print(f"{date} 是工作日吗？{is_workday}")

# 替换成你的 API Key（注册和风天气开发者账号获取）
API_KEY = "057ecbf21d2a4da98c974b7a5ce485aa"
LOCATION = "114.4907,36.6123"  # 可以是城市名，如 "北京" 或经纬度 "116.40,39.90"

# 课表 提醒
@celery_app.task(ignore_result=True,bind=True)
async def remind_s(self: BaseTask):
    dingtalk_url = self.app.conf.get('test_dingtalk_url')
    class_time = {
        '1': {'10_5'  : {'class': '五(4)', 'place': '求真楼 4层'}},
        '2': {'10_5'  : {'class': '五(1)', 'place': '立事楼 1层'},
              '13_50' : {'class': '三(10)', 'place': '求真楼 2层'}},
        '3': {'10_5'  : {'class': '五(2)', 'place': '立事楼 1层'}},
        '4': {'10_5'  : {'class': '三(8)', 'place': '求真楼 2层'},
              '13_50' : {'class': '三(7)', 'place': '求真楼 1层'}},
        '5': {'10_5'  : {'class': '三(9)', 'place': '求真楼 2层'},
              '13_50' : {'class': '五(3)', 'place': '求真楼 3层'}},
    }
    duty_time = {
        '1': {'7_0': '照看午餐🍱', '11_30': '照看午餐🍱'},
        '2': {'7_0': '参加教研会, 携带纸笔!🧑‍🎨🧑‍🎨'},
        '3': {'7_0': '照看延时👩‍💼', '15_30': '照看延时👩‍💼', '19_30': '带身份证'},
        '4': {'7_0': '照看午餐🍛', '11_30': '照看午餐🍛'},
        '5': {'7_0': '站岗💂‍', '9_0': '站岗💂‍', '10_10': '站岗💂‍', '11_0': '站岗💂‍', '14_40': '站岗💂‍', '15_40': '站岗💂‍'},
    }

    water_time = {
        '8_30': '早餐后1小时 (1杯)🥤, 帮助消化，防止饭后血液黏稠度升高。',
        '10_0': '上午工作/学习间隙（1-2杯）🧃🧃, 缓解疲劳，保持专注，避免久坐脱水。',
        '12_50': '午餐后1小时（1杯）🧋, 促进消化吸收，避免饭后腹胀。',
        '14_0': '下午时段（2-3杯）🫗🫗, 缓解午后困倦，维持精力，尤其适合申丹丹本人。',
        '16_0': '下午时段（2-3杯）☕☕, 缓解午后困倦，维持精力，尤其适合申丹丹本人。',
        '17_0': '晚餐前30分钟（半杯）🫖, 控制食欲，避免晚餐过量。',
        '19_0': '晚餐后1小时（1杯）☕, 补充水分，但睡前2小时减少饮水量，避免起夜或水肿。',
        '21_0': '渴了吗? 喝杯水吧🍼🍼!哈哈哈哈!',
    }

    start_time = 1743350400
    start_time = 1746979200

    # 获取某年的所有节假日
    # holidays = calendar.get_holidays(datetime(2025, 1, 1).date(),datetime(2025, 12, 31).date())
    # for holiday in holidays:
    #     print(holiday)
    #
    # sta = _time - start_time
    # print((sta // 86400) % 3)

    # 提取年、月、日、时、分、秒
    # year = now.year
    # month = now.month
    # day = now.day
    now_time = datetime.now()
    date_today=now_time.date()
    hour = now_time.hour
    minute = now_time.minute
    # second = now_time.second
    weekday_num = now_time.weekday()
    print(hour,minute,weekday_num)
    print(class_time.get(str(weekday_num+1), {}).get(f'{hour}_{minute}'))
    print(duty_time.get(str(weekday_num+1), {}).get(f'{hour}_{minute}'))
    print(water_time.get(f'{hour}_{minute}'))

    # 上课
    if calendar.is_workday(date_today) and class_time.get(str(weekday_num+1), {}).get(f'{hour}_{minute}'):
        item = class_time.get(str(weekday_num+1), {}).get(f"{hour}_{minute}", {})
        title = f'申丹丹!要开始上课啦!「{item.get("class")}」({item.get("place")})👩‍🏫👩‍🏫!'
        text = f"##### 申丹丹!要开始上课啦! \n" \
               f"###### 班级: 「{item.get('class')}」({item.get('place')})\n" \
               f"###### 注意: 携带水杯!喝水!\n" \
               f"###### 请关注！\n"
        await dingtalk_helper.send_dingtalk(dingtalk_url, title, text)  # 发送钉钉通知

    # 看午休
    if calendar.is_workday(date_today) and duty_time.get(str(weekday_num+1), {}).get(f'{hour}_{minute}'):

        ex_str = ''
        _time = time.time()
        # if (weekday_num+1 == 1 and ((_time-start_time)//86400)%3 in [0,1]) or (weekday_num+1 == 4 and ((_time-start_time)//86400)%3 in [0,2]):
        #     ex_str = '+ ‼️‼️照看午休‼️‼️'
        if (weekday_num+1 == 1 and ((_time-start_time)//86400)%3 in [0,1]) or (weekday_num+1 == 4 and ((_time-start_time)//86400)%3 in [0,1]):
            ex_str = '+ ‼️‼️照看午休‼️‼️'
        elif weekday_num+1 in [1, 4]:
            ex_str = '+ ❌❌不用❌❌照看午休❌❌'

        title = f"申丹丹!该「{duty_time.get(str(weekday_num+1), {}).get(f'{hour}_{minute}')}{ex_str}」啦!"
        text = f"##### 申丹丹!今天要「{duty_time.get(str(weekday_num+1), {}).get(f'{hour}_{minute}')}{ex_str}」! 千万别忘记奥! \n" \
               f"###### 注意: 吃饱吃饱!\n" \
               f"###### 请关注！\n"
        await dingtalk_helper.send_dingtalk(dingtalk_url, title, text)  # 发送钉钉通知

    # 喝水
    if water_time.get(f'{hour}_{minute}'):

        title = f'申丹丹!申丹丹!该喝水了🚰🚰🚰!'
        text = f"##### 申丹丹!申丹丹!该喝水了🥤🥤! \n" \
               f"###### {hour}: {minute} " + water_time.get(f'{hour}_{minute}') +"\n"\
               f"###### 请关注！\n"
        await dingtalk_helper.send_dingtalk(dingtalk_url, title, text)  # 发送钉钉通知
    return {}


# weather 天气
@celery_app.task(ignore_result=True,bind=True)
async def weather_remind(self: BaseTask):
    """
    早上问候+今日天气
    :param self:
    :return:
    """
    dingtalk_url = self.app.conf.get('test_dingtalk_url')
    now_time = datetime.now()
    # 请求实时天气数据
    url = f"https://devapi.qweather.com/v7/weather/3d?location={LOCATION}&key={API_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            data = await response.json()
    logger.info(data)
    title = f'申丹丹!早上好!☀️☀️'
    text = f"#### 申丹丹!早上好!☀️☀️ \n" \
           f"##### 美好的一天开始啦! 今天是{'「工作日」'if calendar.is_workday(now_time) else '「休息日」'}\n" \
           f"##### 早晨起床后喝一杯水,补充夜间水分流失，促进肠胃蠕动，唤醒新陈代谢。\n" \
           f"##### 接下来播报今日天气: \n" \
           f"###### 城市: 邯郸市丛台区 \n"\
           f"###### 🌤️天气: {data['daily'][0]['textDay']}\n"\
           f"###### 🌡️温度: {data['daily'][0]['tempMin']}°C - {data['daily'][0]['tempMax']}°C\n"\
           f"###### 🌂湿度: {data['daily'][0]['humidity']}%\n"\
           f"###### 💨风速: {data['daily'][0]['windScaleDay']} 级 {data['daily'][0]['windSpeedDay']} m/s\n"\
           f"###### 请关注！  [点击查看](https://www.qweather.com/weather/congtai-101091018.html)\n"
    await dingtalk_helper.send_dingtalk(dingtalk_url, title, text)  # 发送钉钉通知
    return {}

# 晚安
@celery_app.task(ignore_result=True,bind=True)
async def night_remind(self: BaseTask):
    """
    晚睡提醒
    :param self:
    :return:
    """
    dingtalk_url = self.app.conf.get('test_dingtalk_url')
    goodnight_messages = [
        "🌙 晚安，愿你今夜好梦，明天充满活力！",
        "✨ 闭上眼睛，放松身心，明天会更好~",
        "💤 睡个好觉，烦恼都留给明天吧！",
        "🛌 愿你像星星一样安眠，像太阳一样醒来。",
        "🌠 晚安，今天辛苦了，明天继续加油！"
    ]

    title = f'申丹丹!晚上好!✨✨'
    text = f"#### 申丹丹!晚上好! \n" \
           f"##### 该睡觉啦!\n" \
           f"##### {random.choice(goodnight_messages)} \n"
    await dingtalk_helper.send_dingtalk(dingtalk_url, title, text)  # 发送钉钉通知
    return {}


@celery_app.task(ignore_result=True,bind=True)
async def tomorrow_remind(self: BaseTask):
    """
    明日天气+工作日提醒
    :param self:
    :return:
    """
    dingtalk_url = self.app.conf.get('test_dingtalk_url')
    week_day_dic = {0: '一', 1: '二', 2: '三', 3: '四', 4: '五', 5: '六', 6: '日', }
    now_time = datetime.now()
    weekday_num = now_time.weekday()
    date_tow = now_time.date() + timedelta(days=1)
    if calendar.is_workday(date_tow):  # 工作日
        _str = f'明天是 工作日💼⏰⏰ 「星期{week_day_dic.get(weekday_num + 1, weekday_num + 1)}」记得定闹钟奥!⏰⏰'
    else:
        _str = f'明天是 休息日🛋🍃 「星期{week_day_dic.get(weekday_num + 1, weekday_num + 1)}」睡个好觉🛌💤💤'

    # 请求实时天气数据
    url = f"https://devapi.qweather.com/v7/weather/3d?location={LOCATION}&key={API_KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as response:
            data = await response.json()

    title = f'申丹丹!晚上好!✨✨ {_str}'
    text = f"#### 申丹丹!晚上好!✨✨ \n" \
           f"##### {_str}\n " \
           f"##### 明天天气:" \
           f"###### 城市: 邯郸市丛台区 \n" \
           f"###### 🌤天气: {data['daily'][1]['textDay']}\n" \
           f"###### 🌡温度: {data['daily'][1]['tempMin']}°C - {data['daily'][1]['tempMax']}°C\n" \
           f"###### 🌂湿度: {data['daily'][1]['humidity']}%\n" \
           f"###### 💨风速: {data['daily'][1]['windScaleDay']} 级 {data['daily'][1]['windSpeedDay']} m/s\n" \
           f"###### 请关注！  [点击查看](https://www.qweather.com/weather/congtai-101091018.html)\n"
    await dingtalk_helper.send_dingtalk(dingtalk_url, title, text)  # 发送钉钉通知

# 每周二教研 提醒拿笔纸
# 周一周四 看午休 两周一次 31日 27日
# 例假日期
# 土味情话

@celery_app.task(ignore_result=True,bind=True, time_limit=3600*2)
async def send_deepseek(self: BaseTask, content):
    """
    机器人自动回复
    :param self:
    :param content:
    :return:
    """
    dingtalk_url = self.app.conf.get('test_dingtalk_url')
    api_key = 'sk-0dab1a5b7e4e4bfeb84cf4f048fc13b6'
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    ttm_redis = await self.app.ttm.get_redis('ttm_redis')
    messages = [{"role": "system", "content": "你的名字是小张,是一位情感专家并担任日常生活助手,帮助两个用户申丹丹和张谭民增进感情,每个用户在消息前会有标识:申丹丹或张谭民"},
                {"role": "assistant", "content": "你好！我是小张，很高兴能帮助申丹丹和张谭民增进感情。作为你们的日常生活助手，我会用心倾听、提供建议，帮助你们更好地理解彼此、建立更深厚的感情."},
                ]
    rows = await ttm_redis.zrangebyscore('z:deepseek:chat', min=float('-inf'), max=float('inf'))
    await ttm_redis.expire('z:deepseek:chat', 3600*2)
    items = [msgpack.unpackb(row, raw=False) for row in rows]
    messages.extend(items)

    messages.append({"role": "user", "content": content})
    logger.info(messages)
    data = {
        "model": "deepseek-chat",
        "messages": messages
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.deepseek.com/chat/completions", headers=headers, json=data, timeout=3600,
                                    proxy=None) as response:
                logger.info(response.status)
                logger.info(response)
                response = await response.json()
        logger.info(response)

        reply = response["choices"][0]["message"]["content"]
        await ttm_redis.zadd('z:deepseek:chat', now(),
                             msgpack.packb({"role": "user", "content": content}, use_bin_type=True))
        await ttm_redis.zadd('z:deepseek:chat', now(),
                             msgpack.packb({"role": "assistant", "content": reply}, use_bin_type=True))
        await ttm_redis.zadd('z:deepseek:chat_all', now(),
                             msgpack.packb([{"role": "user", "content": content}, {"role": "assistant", "content": reply}], use_bin_type=True))
    except:
        reply = '连接超时, 请联系小张同学处理.'
    title = '小张来啦!'

    print(reply)
    await dingtalk_helper.send_dingtalk(dingtalk_url, title, reply)  # 发送钉钉通知