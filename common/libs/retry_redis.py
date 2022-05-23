from aioredis import Redis, ConnectionClosedError, PipelineError
from aioredis.commands import Pipeline
import backoff


EXCEPTIONS = (ConnectionClosedError, PipelineError)


class RetryPipline(Pipeline):
    
    @backoff.on_exception(backoff.constant, EXCEPTIONS, max_tries=3, logger='ttm.root')
    async def execute(self, *, return_exceptions=False):
        # AssertionError Pipeline already executed. Create new one.
        return await super(RetryPipline, self).execute(return_exceptions=return_exceptions)


class RetryRedis(Redis):

    @backoff.on_exception(backoff.constant, EXCEPTIONS, max_tries=3, logger='ttm.root')
    def execute(self, command, *args, **kwargs):
        return super(RetryRedis, self).execute(command, *args, **kwargs)

    # def pipeline(self):
    #     return RetryPipline(self._pool_or_conn, self.__class__)

    def client_kill(self):
        pass

    def client_reply(self):
        pass

    def monitor(self):
        pass

    def bitfield(self):
        pass
