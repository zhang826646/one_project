from sanic.response import json
from sanic_openapi import doc
from sqlalchemy import and_, func
from common.exceptions import ApiCode
from common.libs.comm import now
from common.libs.aio import run_sqlalchemy
from common.dao.book import Book


@doc.summary('书籍列表')
@doc.consumes(
    doc.JsonBody({
        'page'          : doc.Integer('页码'),
        'limit'         : doc.Integer('每页条数'),
        'catalog_id'    : doc.Integer('版块ID'),
        'postName'      : doc.String('帖子标题'),
        'status'  : doc.String('状态'),
    }), content_type='application/json', location='body', required=True
)
async def book_list(request):
    page = request.json.get('pageNum', 1)
    limit = request.json.get('pageSize', 15)
    title = request.json.get('bookName')
    _type = request.json.get('bookType')
    status = request.json.get('status')

    beginTime = request.json.get('beginTime')
    endTime = request.json.get('endTime')
    # cond = and_(cond, PayRecord.created_at.between(int(beginTime), int(endTime)))


    offset = (page - 1) * limit
    lists = []

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    cond = True

    if title:
        cond = Book.title.like(f'%{title}%')
    if _type:
        cond = and_(cond, Book.booktpye == _type)

    cond = and_(cond, Book.delete == 0)

    @run_sqlalchemy()
    def get_post_list_data(db_session):
        return db_session.query(Book) \
            .filter(cond) \
            .order_by(Book.update_time.desc()) \
            .offset(offset).limit(limit) \
            .all()

    rows = await get_post_list_data(ttm_sql)

    for row in rows:

        lists.append({
            'id'               : row.id,
            'title'       : row.title,
            'author'             : row.author ,
            'publish'              : row.publish,
            'booktpye'             : row.booktpye,
            'pages'          : row.pages,
            'book_url'          : row.book_url,
            'update_time'           : row.update_time,

        })

    total = ttm_sql.query(func.count(Book.id)).filter(cond).scalar()
    data = {
        'code'        : ApiCode.SUCCESS,
        'current_page': page,
        'page_size'   : limit,
        'total'       : total,
        'data'        : lists
    }
    return json(data)

@doc.summary('编辑帖子')
async def save_book(request):
    book_id = request.json.get('id')
    title = request.json.get('title')
    author = request.json.get('author')
    publish = request.json.get('publish')
    booktpye = request.json.get('booktpye')
    pages = request.json.get('pages')
    book_url = request.json.get('book_url')
    cover = request.json.get('cover')


    ttm_sql = request.app.ttm.get_mysql('ttm_sql')
    if book_id:
        item = ttm_sql.query(Book).filter(Book.id == book_id).first()
    else:
        item = Book()
        item.update_time=now()
        ttm_sql.add(item)

    item.title = title
    item.author = author
    item.publish = publish
    item.booktpye = booktpye
    item.pages = pages
    item.book_url = book_url
    item.cover = cover

    ttm_sql.commit()


    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})



@doc.summary('书籍详情')
@doc.consumes(
    doc.JsonBody({
        'page'          : doc.Integer('页码'),
        'limit'         : doc.Integer('每页条数'),
        'catalog_id'    : doc.Integer('版块ID'),
        'postName'      : doc.String('帖子标题'),
        'status'  : doc.String('状态'),
    }), content_type='application/json', location='body', required=True
)
async def book_detali(request,id):

    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    cond = Book.id == id

    @run_sqlalchemy()
    def get_book_data(db_session):
        return db_session.query(Book) \
            .filter(cond) \
            .first()

    row = await get_book_data(ttm_sql)


    item={
        'id'               : row.id,
        'title'       : row.title,
        'author'             : row.author ,
        'publish'              : row.publish,
        'booktpye'             : row.booktpye,
        'pages'          : row.pages,
        'book_url'          : row.book_url,
        'update_time'           : row.update_time,

    }

    data = {
        'code'        : ApiCode.SUCCESS,
        'data'        : item
    }
    return json(data)



@doc.summary('更新数据')
async def delete_book(request):
    book_id_list = request.json.get('book_id_list')
    print(book_id_list)
    if type(book_id_list) == int:
        book_id_list= [book_id_list]
    print(book_id_list)
    ttm_sql = request.app.ttm.get_mysql('ttm_sql')

    books = ttm_sql.query(Book).filter(Book.id.in_(book_id_list)).all()

    for book in books:
        print(book.id)
        book.delete = 1

    ttm_sql.commit()
    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})


@doc.summary('更新图书')
async def updata_book(request):
    # await request.app.ttm.celery.send_task('apps.tasks.group.build_follower_list', args=())
    print(request.app.ttm.celery)
    print(request.app.celery)
    await request.app.celery.send_task('apps.tasks.book.book_updata', args=())
    return json({'code': ApiCode.SUCCESS, 'msg': '操作成功'})
