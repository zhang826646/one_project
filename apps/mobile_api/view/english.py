
import re
import ujson
import random
import time
import lxml.html
from sanic.exceptions import InvalidUsage
from sanic.response import json
from sanic_openapi import doc
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import aliased
from common.exceptions import ApiError, ApiCode
from common.libs.comm import total_number, now, to_int, inc_count
from common.libs.aio import run_sqlalchemy
from common.helper.validator_helper import validate_params, CharField, IntegerField, ListField, DictField
from common.dao.mobile import Specialty, Course, EN_word ,Answer
from common.dao.member import TtmMember


@doc.summary('专业列表')
@doc.consumes()
@validate_params(
    IntegerField(name='page', required=False, min_value=1),
    IntegerField(name='limit', required=False, min_value=1),
)
async def specialty_list(request):
    print(request.__dict__)
    page = request.valid_data.get('pageNum', 1)
    limit = request.valid_data.get('pageSize', 15)
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    offset = (page - 1) * limit
    lists = []

    cond = True

    # if _type:
    #     cond = CirclePost.deleted == status

    @run_sqlalchemy()
    def get_specialty_data(db_session):
        return db_session.query(Specialty).filter(cond).offset(offset).limit(limit).all()

    rows = await get_specialty_data(ttm_sql)

    for row in rows:
        lists.append({
            'id'       : row.id,
            'title'    : row.title,
            'brief'    : row.brief,
            'quantity' : row.quantity,
        })

    total = ttm_sql.query(func.count(Specialty.id)).filter(cond).scalar()
    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'total'       : total,
        'data'        : lists
    }
    return json(data)


@doc.summary('单词')
@doc.consumes()
@validate_params(
    IntegerField(name='page', required=False, min_value=1),
    IntegerField(name='limit', required=False, min_value=1),
)
async def english_word(request):
    print(request.__dict__)
    page = request.valid_data.get('page', 1)
    limit = request.valid_data.get('limit', 1)
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    offset = (page - 1) * limit
    lists = []

    cond = EN_word.specialty_id == Course.specialty_id
    cond = and_(cond, Course.member_id == 1000008)

    # if _type:
    #     cond = CirclePost.deleted == status

    @run_sqlalchemy()
    def get_specialty_data(db_session):
        return db_session.query(EN_word,Course).filter(cond).offset(offset).limit(limit).all()

    rows = await get_specialty_data(ttm_sql)
    pattern2 = re.compile(r'([a-z/]+\..+?\s)')
    data={}
    if limit == 1:
        for word, v in rows:
            zh_words = pattern2.findall(word.zh_word)
            data = {
                'id'       : word.id,
                'en_word'    : word.en_word,
                'zh_word'    : zh_words,
                'soundmark' : word.soundmark,
            }
    else:
        for word,v in rows:
            zh_words = pattern2.findall(word.zh_word)
            lists.append({
                'id'       : word.id,
                'en_word'    : word.en_word,
                'zh_word'    : zh_words,
                'soundmark' : word.soundmark,
            })

    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'data'        : data,
        'list'        : lists
    }
    return json(data)
