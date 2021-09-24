from apps.base import App
from apps.base_url import base_bp
from apps.web_api.urls import blueprint

app = App(__name__)
app.static('/favicon.ico', './static/favicon.ico')

app.blueprint(blueprint)
app.blueprint(base_bp)
app.config.update({'aes_key': 'i7!4cH3!IjgE8Rf0'})