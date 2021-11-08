from sanic.response import redirect
from importlib import import_module
from sanic_openapi import swagger_blueprint
import argparse
import logging.config
from apps import mako,os

parser = argparse.ArgumentParser(description="Start The Leisu APP Server")

parser.add_argument('-app', '--application', default='web_api', dest='app',
                    help='启动的APP，可选项[app_api|web_api|web_internal_api|mobile_api|admin_api]', type=str)

parser.add_argument('-env', '--environment', default='dev', dest='env',
                    help='配置文件，可选项[local|dev|prod]', type=str)

parser.add_argument('-port', '--port', dest='port',
                    help='port 端口', type=int)

parser.add_argument('-work', '--workers', dest='work',
                    help='workers 进程数量', type=int)

start_args = parser.parse_args()

# 匹配 APP 与配置文件
app = import_module(f'apps.{start_args.app}.app').app
app.config.update(import_module(f'config.{start_args.env}').config)
paths=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
mako.init_app(app,pkg_path=paths,context_processors=())

app.config.update({'LOGO': f'\n\n                   api\n        '
                           f' APP:<<{start_args.app}>>  ENV:<<{start_args.env}>>\n'
                           f'    Debug:{app.config.get("debug")}    ACCESS_LOG:{app.config.get("ACCESS_LOG")}'
                           f'    Workers:{start_args.work if start_args.work else app.config.get("workers")}\n\n '
                   })

# 非Debug状态下打印信息
if not app.config.debug:
    print(app.config.get('LOGO'))

# 初始化自定义日志
logging.config.dictConfig(app.config.logging_config)
logger = logging.getLogger('leisu.root')


# 注册 Swagger Blueprint
app.blueprint(swagger_blueprint)
app.config['API_LICENSE_NAME'] = f'Leisu  【{start_args.app}】'
logger.info('注册 Swagger')

# 非生产环境 首页重定向到 Swagger
if app.config.get('env') != 'prod':
    @app.route('/', strict_slashes=True)
    async def swagger(request):
        return redirect('/swagger')


if __name__ == '__main__':
    app.run(
        host=app.config.host,
        port=start_args.port if start_args.port else app.config.get('port'),
        debug=app.config.debug,
        workers=start_args.work if start_args.work else app.config.get('workers')
    )
