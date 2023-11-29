import asyncio
from threading import Event
from celery.utils.dispatch.signal import Signal
from celery_pool_asyncio import pool
from celery.utils.dispatch.signal import NO_RECEIVERS, sys, logger


class AsyncToSync:
    __slots__ = (
        'coro',
        'event',
        'error',
        'result',
    )

    def __init__(self, coro):
        self.coro = coro
        self.event = Event()

    def __call__(self):
        coro = self.__wrapper()
        pool.run(coro)
        self.event.wait()

    async def __wrapper(self):
        try:
            self.result = await self.coro
            self.error = False
        except Exception as e:
            self.result = e
            self.error = True
        finally:
            self.event.set()


def handle_error(self, receiver, exc):
    if not hasattr(exc, '__traceback__'):
        exc.__traceback__ = sys.exc_info()[2]
    logger.exception('Signal handler %r raised: %r', receiver, exc)
    return receiver, exc


def send_iter(self, sender, **named):
    if not self.receivers or \
            self.sender_receivers_cache.get(sender) is NO_RECEIVERS:
        return

    for receiver in self._live_receivers(sender):
        try:
            if asyncio.iscoroutinefunction(receiver):
                coro = receiver(signal=self, sender=sender, **named)
                waiter = AsyncToSync(coro)
                waiter()  # blocking

                if waiter.error:
                    yield handle_error(self, receiver, waiter.result)
                    continue

                yield receiver, waiter.result
            else:
                response = receiver(signal=self, sender=sender, **named)
                yield receiver, response

        except Exception as exc:  # pylint: disable=broad-except
            yield handle_error(self, receiver, exc)


def send(self, sender, **named):
    return list(send_iter(self, sender, **named))


Signal.send = send
