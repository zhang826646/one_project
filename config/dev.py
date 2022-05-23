import sys


config = dict(
    # Swagger
    API_SCHEMES=['https', 'http'],
    # Sanic App run config
    host='0.0.0.0',
    port=30001,
    debug=True,
    ACCESS_LOG=True,
    workers=1,

    # Celery 配置
# Celery 配置
    # task_acks_late = True,
    task_serializer='json',
    # result_backend='disabled://',
    # result_serializer='json',
    result_expires=None,
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=False,
    imports=['apps.tasks', 'apps.tasks.celery'],
    task_soft_time_limit=600,
    task_default_rate_limit='1500/m',
    # CELERY_DEFAULT_QUEUE='dev_celery',
    broker_url='redis://:qxiaolu@8.142.187.110:6379/15',  # 使用Redis作为消息代理
    result_backend='redis://:qxiaolu@8.142.187.110:6379/15',  # 把任务结果存在了Redis
    # BROKER_URL='redis://:qxiaolu@localhost:6379/15',  # 使用Redis作为消息代理
    # CELERY_RESULT_BACKEND='redis://:qxiaolu@localhost:6379/15',  # 把任务结果存在了Redis
    # # CELERY_TASK_SERIALIZER = 'msgpack' # 任务序列化和反序列化使用msgpack方案
    # CELERY_RESULT_SERIALIZER='json',  # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON
    # # CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 , # celery任务结果有效期
    # CELERY_ACCEPT_CONTENT=['json', 'msgpack'],  # 指定接受的内容类型
    # CELERY_TIMEZONE='Asia/Shanghai',  # celery使用的时区
    # CELERY_ENABLE_UTC=True,  # 启动时区设置
    # CELERYD_LOG_FILE="/var/log/celery/celery.log",  # celery日志存储位置


    # 全局自定义日志配置
    logging_config={
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            'ttm.root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': sys.stdout,
            }
        },
        'formatters': {
            'generic': {
                'format': '%(asctime)s [%(process)d] [%(levelname)s] [%(pathname)s line:%(lineno)s] %(message)s',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
                'class': 'logging.Formatter',
            }
        },
    },
    mysql={
            'ttm_sql': {
                'engine': 'mysql+pymysql://ll:Ll123???@8.142.187.110:3306/TTM?charset=utf8mb4',
                'echo'  : False,
            },
        },

    redis={
        'ttm_redis': {
            'address': 'redis://8.142.187.110:6379',
            'password': 'qxiaolu',
            'host': '8.142.187.110',
            'port': 6379
        },
    },
)

# # 合并基础配置
# config.update(base_config)