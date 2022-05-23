import argparse
import socket
from importlib import import_module
from apps.tasks import celery
from apps.tasks.celery import celery_app
from celery.utils.imports import instantiate

parser = argparse.ArgumentParser(description="Start The TT/m Celery")

parser.add_argument('-env', '--environment', default='dev', dest='env',
                    help='配置文件，可选项[local|dev|prod]', type=str)

parser.add_argument('-a', '--action', default='worker', dest='action',
                    help='Celery动作可选项[worker|beat]', type=str)

parser.add_argument('-q', '--queues', default='', dest='queues',
                    help='路由队列', type=str)

parser.add_argument('-p', '--port', default='80', dest='flower_port',
                    help='Flower的端口', type=str)

parser.add_argument('-l', '--level', default='INFO', dest='log_Level',
                    help='日志等级[DEBUG, INFO, WARNING, ERROR]', type=str)

start_args = parser.parse_args()

# 初始化Celery配置文件
celery_app.conf.update(import_module(f'config.dev').config)
celery_app.config = celery_app.conf  # 兼容Sanic配置文件

if __name__ == '__main__':
    if start_args.action == 'worker':
        from common.libs import celery_patch  # patch
        node_name = celery_app.conf.get('node_name')
        queues = celery_app.conf.get('task_default_queue')
        if start_args.queues:
            queues = f'{start_args.env}_celery_{start_args.queues}'
        celery.NODE_NAME = socket.gethostname()
        argv = ['worker', '-A', 'apps.tasks', '-P', 'celery_pool_asyncio:TaskPool', '-n', f'{node_name}@%h',
                '-Q', queues, '-l', start_args.log_Level]
        instantiate('celery.bin.worker:worker', app=celery_app).execute_from_commandline(argv)

