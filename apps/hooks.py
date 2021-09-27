
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker


import aioredis
import asyncio
import uuid
import redis
import threading
import asyncio
import os



class StartHook:
    def __init__(self, _app, _loop=None):
        self.app = _app
        self.loop = _loop if _loop else asyncio.get_event_loop()
        self.mysql_instance = {}    #mysql 连接实例
        self.redis_instance = {}
        self.redis_instance_sync = {}
        self.alilog_instance = {}
        self.es_instance = {}
        self.qqwry = None
        self.mqtt = None
        self.celery = None
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_mysql(self,name):
        """
        获取 Mysql sqlalchemy scoped_session 连接池实例
        :param name: 配置文件里的Mysql配置名
        :return: sqlalchemy scoped_session 连接池实例
        :rtype: scoped_session
        """
        def scopefunc():
            try:
                return asyncio.Task.current_task()  # Sanic 使用当前Task来唯一 Sqlalchemy Session
            except RuntimeError:
                return threading.current_thread()  # run_on_executor 使用当前Threading来唯一 Sqlalchemy Session

        instance = self.mysql_instance.get(name)
        if not instance:
            instance = scoped_session(
                sessionmaker(
                    bind=create_engine(
                        self.app.config.mysql[name].get('engine'),
                        echo=self.app.config.mysql[name].get('echo'),
                        # 设置连接池断开连接的时间,Mysql会自动断开超过8小时的连接
                        pool_recycle=600,
                        # 设置获取连接池的超时时间,当超时 max_overflow 数量时其他连接会等待
                        pool_timeout=300,
                        # 允许最大连接的数量,-1表示不限制。
                        max_overflow=300,
                        # 次签出时测试连接的活动性,防止Timeout
                        # pool_pre_ping=True,
                        # 设置底层DBAPI的数据库连接超时时间
                        connect_args={'connect_timeout': 3}
                    ),
                ), scopefunc=scopefunc
            )
            self.mysql_instance[name] = instance
        return instance

