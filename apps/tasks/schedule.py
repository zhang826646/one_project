from celery.schedules import crontab

# from apps.tasks import schedule
# 开发环境定时任务
dev_beat_schedule = {
    # 'ok': {'task': 'apps.tasks.ok.buil_billiards_list', 'schedule': 10, 'args': ()},
    # 'ok': {'task': 'apps.tasks.ok.w_billiards_list', 'schedule': crontab(minute='0',hour='*/1'), 'args': ()},
    # 'ok_sjz': {'task': 'apps.tasks.ok_sjz.w_billiards_list', 'schedule': crontab(minute='0',hour='*/1'), 'args': ()},
    # 'ok_up_file': {'task': 'apps.tasks.ok.update_execl', 'schedule': crontab(minute='10',hour='*/1'), 'args': ()},
    # 'ok_sjz_up_file': {'task': 'apps.tasks.ok_sjz.update_execl', 'schedule': crontab(minute='10',hour='*/1'), 'args': ()},
    # 'ok_sjz_up_file': {'task': 'apps.tasks.ok_sjz.update_execl', 'schedule': crontab(minute='10',hour='*/1'), 'args': ()},
    'remind_s': {'task': 'apps.tasks.dandan.remind_s', 'schedule': crontab(minute='*'), 'args': ()},
    'weather_remind': {'task': 'apps.tasks.dandan.weather_remind', 'schedule': crontab(hour='7', minute='0'), 'args': ()},
    'night_remind': {'task': 'apps.tasks.dandan.night_remind', 'schedule': crontab(minute='30', hour='22'), 'args': ()},
}