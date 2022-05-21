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
    # 全局自定义日志配置
    logging_config={
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            'leisu.root': {
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

