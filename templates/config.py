import distutils.spawn
import os
from pathlib import Path
from typing import List, Tuple

import yaml


class AttrDict(dict):

    def __init__(self, *args, **kwargs) -> None:
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self




REACT_PROMPT = '喜欢这篇文章吗? 记得给我留言或订阅哦'
HERE = Path(__file__).parent.absolute()

SITE_TITLE = 'TTm'
USE_YAML=True
GOOGLE_ANALYTICS = ''
SENTRY_DSN = ''
BLOG_URL = 'https://www.baidu.com'
BEIAN_ID=''

# [(Endpoint, Name, IconName, Color), ...]
SITE_NAV_MENUS=[
    {'endpoint':'/index','name':'首页'},
    {'endpoint':'/index','name':'动态'},
    {'endpoint':'/index','name':'专题'},
    {'endpoint':'/index','name':'归档'},
    {'endpoint':'/index','name':'标签'},
    {'endpoint':'/index','name':'搜索'},
    {'endpoint':'/index','name':'登录/注册'},
    {'endpoint':'/index','name':'头像','color': '#fc6423'},

]



REACT_PROMPT = '喜欢这篇文章吗? 记得给我留言或订阅哦'
COMMENT_REACTIONS = ['heart', 'upvote']
