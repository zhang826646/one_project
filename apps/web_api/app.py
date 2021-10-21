from apps.base import App
from apps.base_url import base_bp
from apps.web_api.urls import blueprint
import os
import logging

# from sanic_jinja2 import Environment,FileSystemLoader,select_autoescape

print(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static'))
app = App(__name__)
# app.static('/favicon.ico', './static/favicon.ico')
app.static('/static',os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static'))
app.blueprint(blueprint)
app.blueprint(base_bp)

# app.config.update({'aes_key': 'i7!4cH3!IjgE8Rf0'})
# @app.listener('before_server_start')
# async def app_api_start(_app, _loop):
#     logger = logging.getLogger('leisu.root')
#     logger.info('APP_API 启动前钩子')
#     _app.template_env = Environment(
#         loader=FileSystemLoader(f'{_app.leisu.base_dir}/apps/app_api/templates'),
#         autoescape=select_autoescape(['html', 'xml']),
#         enable_async=True  # 模板支持异步
#     )
