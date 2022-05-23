import asyncio
import time
import inspect
import traceback
import copy
import msgpack
from celery import Celery
from functools import wraps
from celery.app.task import Task
from apps.hooks import StartHook
from common.exceptions import TaskExecuteError

from common.libs.comm import set_count, get_count, reset_count, md5, inc_count
from celery.signals import task_prerun, worker_init, worker_shutting_down
from celery.utils.log import get_task_logger
from celery.exceptions import Reject, Retry
from celery.utils.serialization import raise_with_context


logger = get_task_logger(__name__)
NODE_NAME = ''


@task_prerun.connect
def add_start_time(sender=None, headers=None, body=None, **kwargs):
    sender.start_time = time.time()


@worker_init.connect
async def db_conn_init(sender=None, headers=None, body=None, **kwargs):
    print('db_conn_init is running')


@worker_shutting_down.connect
async def db_conn_shutdown(sender=None, headers=None, body=None, **kwargs):
    print('db_conn_shutdown is running')


class MyCelery(Celery):
    task_cls = 'apps.tasks.celery:BaseTask'


class BaseTask(Task):

    def run(self, *args, **kwargs):
        super(BaseTask, self).run(*args, **kwargs)

    def __init__(self):
        super(BaseTask, self).__init__()
        self.explain = None

    async def retry(self, args=None, kwargs=None, exc=None, throw=True, eta=None, countdown=None,
                    max_retries=None, **options):
        request = self.request
        retries = request.retries + 1
        max_retries = self.max_retries if max_retries is None else max_retries

        # Not in worker or emulated by (apply/always_eager),
        # so just raise the original exception.
        if request.called_directly:
            # raises orig stack if PyErr_Occurred,
            # and augments with exc' if that argument is defined.
            raise_with_context(exc or Retry('Task can be retried', None))

        if not eta and countdown is None:
            countdown = self.default_retry_delay

        is_eager = request.is_eager
        signature = self.signature_from_request(
            request, args, kwargs,
            countdown=countdown, eta=eta, retries=retries,
            **options
        )

        if max_retries is not None and retries > max_retries:
            if exc:
                # On Py3: will augment any current exception with
                # the exc' argument provided (raise exc from orig)
                raise_with_context(exc)
            raise self.MaxRetriesExceededError(
                "Can't retry {0}[{1}] args:{2} kwargs:{3}".format(
                    self.name, request.id, signature.args, signature.kwargs
                ), task_args=signature.args, task_kwargs=signature.kwargs
            )

        ret = Retry(exc=exc, when=eta or countdown)

        if is_eager:
            # if task was executed eagerly using apply(),
            # then the retry must also be executed eagerly.
            signature.apply().get()
            if throw:
                raise ret
            return ret

        try:
            await signature.apply_async()
        except Exception as exc:
            raise Reject(exc, requeue=False)
        if throw:
            raise ret
        return ret

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        super(BaseTask, self).after_return(status, retval, task_id, args, kwargs, einfo)
        # self.app.ttm.remove_mysql_session()

    def on_success(self, retval, task_id, args, kwargs):
        super(BaseTask, self).on_success(retval, task_id, args, kwargs)


    def on_retry(self, exc, task_id, args, kwargs, einfo):
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)


    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)


    async def add_sls_log(self, **kwargs):
        if 'refresh_filecache' in self.name:
            if await inc_count(self.app, f'sls:{self.name}', ttl=86400) % 10 == 0:
                pass
            else:
                return
        current = time.time()
        redis_normal = await self.app.ttm.get_redis('normal')
        await redis_normal.zadd('z:sls:celery_log', current, msgpack.packb(kwargs))


celery_app = MyCelery('ttm')
celery_app.ttm = StartHook(celery_app)
celery_app.ttm.celery = celery_app


def task_retry(exc=(Exception,), max_retries=2, countdown=None, jitter=None):
    """
    任务重试
    :param exc:
    :param max_retries: 最大重试次数
    :param countdown: 下次重试时间
    :param jitter: jitter为可执行对象时，countdown参数被忽略，下次重试时间为 jitter(n) 得到的值, n为当前重试次数
    :return:
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self: BaseTask, *args, **kwargs):
            try:
                r = await func(self, *args, **kwargs)
                return r
            except exc as e:
                if callable(jitter):
                    cd = jitter(self.request.retries+1)
                else:
                    cd = countdown
                await self.retry(exc=e, countdown=cd, max_retries=max_retries)
        return wrapper
    return decorator


def task_explain(comment='', explains=None):
    """
    :param str comment: 描述语句
    :param dict explains:  comment的占位符变量,如果值是None,变量值取该方法的参数值,如果是字典,则取该方法的参数值在此字典中的值
    :return:
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self: BaseTask, *args, **kwargs):
            try:
                params = {}
                for k, v in explains.items():
                    if k in kwargs:
                        value = kwargs.get(k)
                    elif k in inspect.getfullargspec(func).args:
                        args_idx = inspect.getfullargspec(func).args.index(k) - 1
                        value = args[args_idx]
                    elif k in func.__kwdefaults__:
                        value = func.__kwdefaults__.get(k)
                    else:
                        value = ''
                    if v is None:
                        params[k] = value
                    elif isinstance(v, dict):
                        params[k] = v.get(value)
                    else:
                        params[k] = ''
                self.explain = comment.format(**params)
            except Exception as e:
                logger.error(traceback.format_exc())

            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


def task_concurrent_limit(countdown=None, max_retries=2, silent=False):
    """
    任务并发限制
    :param countdown: 几秒后重试
    :param max_retries:  最大重试次数
    :param silent:  报错是否发送到钉钉
    :return:
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self: BaseTask, *args, **kwargs):
            key = md5(f'{self.app.config.env}|{self.name}|{args}|{kwargs}')
            count = await get_count(self.app, f'task_concurrent_limit:{key}')
            if count > 0:
                exc = TaskExecuteError(msg='任务执行并发限制', silent=silent)
                if countdown:
                    await self.retry(countdown=countdown, exc=exc, max_retries=max_retries)
                else:
                    raise exc
            await set_count(self.app, f'task_concurrent_limit:{key}', ttl=60, amount=1)
            try:
                return await func(self, *args, **kwargs)
            finally:
                await reset_count(self.app, f'task_concurrent_limit:{key}')
        return wrapper
    return decorator
