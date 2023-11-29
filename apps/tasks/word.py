import datetime

from apps.tasks.celery import celery_app, BaseTask
from common.dao.mobile import EN_word
from common.libs.comm import now
from common.libs.aio import run_sqlalchemy
from sqlalchemy import and_, func, or_, distinct, case
import os
import re


@celery_app.task(bind=True)
async def word_updata(self: BaseTask):

    ttm_sql = self.app.ttm.get_mysql('ttm_sql')

    # 读取文档
    with open(r'/data/one/one_project/static/中考英语词汇表.txt','r',encoding='utf-8') as bok:
        bok_de=bok.readlines()

    word_objs = []
    for rows in bok_de:
        pattern = re.compile(r'(\[.+\])')
        result = pattern.findall(rows)
        if result:
            word_detail= rows.split(result[0],1)
            word=word_detail[0]
        elif len(rows)<5:
            continue
        else:
            word= rows

        # pattern2 = re.compile(r'([a-z/]+\..+?\s)')
        # paraphrase = pattern2.findall(result[-1])
#
# #
#         en_word = EN_word()
#         en_word.specialty_id = 1
#         en_word.en_word = word
#         if result:
#             en_word.zh_word = result[-1]
#             en_word.soundmark = result[0]
#         en_word.updated_at=datetime.datetime.fromtimestamp(now())
#         word_objs.append(en_word)
#
#         ttm_sql.bulk_save_objects(word_objs)
#         ttm_sql.commit()

        item = {
            'specialty_id': 1,
            'en_word'     : word,
            'zh_word'     : word_detail[-1] if result else '',
            'soundmark'   : result[0] if result else '',
            'updated_at'  : datetime.datetime.fromtimestamp(now())
        }
        print(item)
        is_new, columns, row = EN_word.upsert(
            ttm_sql, EN_word.en_word == item['en_word'], attrs=item
        )
        if columns:
            word_objs.append(row)

    ttm_sql.bulk_save_objects(word_objs)
    ttm_sql.commit()


    print('任务结束')
#
#
