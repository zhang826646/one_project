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

# [(Endpoint, Name, IconName, Color), ...]
SITE_NAV_MENUS: List[Tuple] = []
BEIAN_ID = ''


REACT_PROMPT = '喜欢这篇文章吗? 记得给我留言或订阅哦'
COMMENT_REACTIONS = ['heart', 'upvote']
