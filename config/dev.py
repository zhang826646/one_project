import sys


config = dict(
    # Swagger
    API_SCHEMES=['https', 'http'],
    # Sanic App run config
    host='0.0.0.0',
    port=8000,
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
            'min_sql': {
                'engine': 'mysql+pymysql://root:@180.76.163.190:3306/one_project?charset=utf8mb4',
                'echo'  : False,
            },
        },
)

