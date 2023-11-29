import datetime

from apps.tasks.celery import celery_app, BaseTask
from common.dao.mobile import EN_word
from common.libs.comm import now
from common.libs.aio import run_sqlalchemy
from common.dao.circle import CirclePost
from sqlalchemy import and_, func, or_, distinct, case
import os
import re


@celery_app.task(bind=True)
async def fix_post(self: BaseTask):

    ttm_sql = self.app.ttm.get_mysql('ttm_sql')

    post_list = ttm_sql.query(CirclePost).all()
    for i in post_list:
        new_string = i.content.replace("http://cdn.qxiaolu.club/", "http://cdn.iuttm.cn/")
        i.content = new_string
    ttm_sql.commit()