import argparse
import socket
from importlib import import_module
from apps.tasks import celery_app


parser = argparse.ArgumentParser(description="Start The TT/m Celery")

parser.add_argument('-env', '--environment', default='dev', dest='env',
                    help='配置文件，可选项[local|dev|prod]', type=str)

parser.add_argument('-a', '--action', default='beat', dest='action',
                    help='Celery动作可选项[worker|beat]', type=str)

parser.add_argument('-q', '--queues', default='', dest='queues',
                    help='路由队列', type=str)

parser.add_argument('-p', '--port', default='80', dest='flower_port',
                    help='Flower的端口', type=str)

parser.add_argument('-l', '--level', default='DEBUG', dest='log_Level',
                    help='日志等级[DEBUG, INFO, WARNING, ERROR]', type=str)

start_args = parser.parse_args()

# 初始化Celery配置文件
config = import_module(f'config.{start_args.env}').config
celery_app.conf.update(config)
celery_app.config = celery_app.conf  # 兼容Sanic配置文件

if __name__ == '__main__':
    import gevent.monkey
    gevent.monkey.patch_all(
        thread=False,  # 避免与异步库冲突
        socket=True,
        time=True,
        select=True,
        ssl=True
    )
    if start_args.action == 'worker':
        node_name = celery_app.conf.get('node_name', 'worker')
        queues = start_args.queues or celery_app.conf.get('task_default_queue', 'default')

        argv = [
            'worker',
            f'--hostname={node_name}@%h',
            f'--queues={queues}',
            f'--loglevel={start_args.log_Level}',
            '--pool=gevent',
            '--without-gossip',
            '--without-mingle',
            '--without-heartbeat',
            '--concurrency=100'
            ]

        # 直接调用worker_main
        celery_app.worker_main(argv=argv)

    elif start_args.action == 'beat':
        argv = [
            '-A', 'apps.tasks',  # 指定Celery应用模块
            'beat',
            '--max-interval=5',
            '--schedule=celerybeat-schedule',
            f'--loglevel={start_args.log_Level}',
            '--pidfile=celerybeat.pid'
        ]

        # 直接调用start
        celery_app.start(argv=argv)