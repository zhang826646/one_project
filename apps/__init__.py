
from sanic_mako import SanicMako,os,render_template

# paths=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
# jinja=SanicJinja2(pkg_path='D:/MyProject/one_project/templates')
mako = SanicMako()

import logging

logger = logging.getLogger('TTM')


