import asyncio
import functools
import concurrent.futures
import logging

logger = logging.getLogger('ttm.root')


# 协程装饰器 Future 对象
def run_on_executor():
    """
    :return: type asyncio.Future
    """

    # 参考文档：https://docs.python.org/zh-cn/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            # loop = asyncio.get_running_loop()
            loop = asyncio.get_event_loop()
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     return await loop.run_in_executor(executor, functools.partial(fn, *args, **kwargs))

            # loop.run_in_executor 这个方法返回一个 asyncio.Future 对象, 使之可以使用 await 关键字
            # 让本身不支持asyncio（可等待对象）的方法也能使用异步 await
            return await loop.run_in_executor(None, functools.partial(fn, *args, **kwargs))

        return wrapper

    return decorator


def run_sqlalchemy():
    def decorator(fn):
        @run_on_executor()
        def run_sql(db_session, *args, **kwargs):
            try:
                data = fn(db_session, *args, **kwargs)
                return data
            except Exception as e:
                raise e
            finally:
                db_session.remove()
        return run_sql
    return decorator
