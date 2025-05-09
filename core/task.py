import time

from common.libs.comm import md5, inc_count, reset_count


class TaskManager(object):

    @staticmethod
    async def send_task(app, name, args=None, kwargs=None, countdown=None, force=False, **options):
        key = md5(f'{name}|{args}|{kwargs}')
        task_id = f'{key}-{int(time.time()*1000000)}'
        if not force and countdown:
            ttl = max(0, countdown - 1)
            if not ttl or await inc_count(app, f'send_task:{key}', ttl=ttl, reset_ttl=False) == 1:
                return await app.ttm.celery.send_task(name, args=args, kwargs=kwargs, countdown=countdown, task_id=task_id, **options)
        else:
            return await app.ttm.celery.send_task(name, args=args, kwargs=kwargs, countdown=countdown, task_id=task_id, **options)

    @staticmethod
    async def revoke(app, task_id):
        app.leisu.celery.control.revoke(task_id=task_id)

        p = task_id.split('-')
        if len(p) == 2:
            key = p[0]
            await reset_count(app, f'send_task:{key}')