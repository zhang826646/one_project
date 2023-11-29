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

