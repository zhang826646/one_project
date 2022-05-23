
from aligo import Aligo,Auth
import fitz
from apps.tasks.celery import celery_app,BaseTask
from common.dao.book import Book
from common.libs.comm import now
from qiniu import Auth, put_file, etag
from common.helper.qiniu_helper import get_upload_token,upload_img,upload_image,upload
from common.libs.aio import run_sqlalchemy


@celery_app.task(bind=True)
async def book_updata(self: BaseTask,file_id=None ):
    """
    图书信息入库
    """
    token = await get_upload_token('books', False, size=1000)
    ttm_sql = self.app.ttm.get_mysql('ttm_sql')

    # auth = Auth(name='refresh_token', refresh_token='dd2e8fd6320240bbabdf2db372d7ef2a')
    ali =Aligo()

    file_id='616fb7f8d13949bc36924668883e2c3bed9fad6b'
    # 获取用户信息
    user = ali.get_user()
    if not user:
        pass
    # 获取网盘根目录文件列表
    root_file_list = ali.get_file_list()
    print( root_file_list)
    file_list = ali.get_file_list(file_id)
    print(file_list)

    @run_sqlalchemy()
    def get_book_data(db_session,title):
        return db_session.query(Book) \
            .filter(Book.title == title) \
            .first()

    for i in file_list[:1]:
        if i.type=='file':
            file_url=i.download_url
            file_name = i.name
            book_name = file_name.split('.')[0]
            cover_name = book_name + '.png'
            cover_path = f'/data/one/book_data/{cover_name}'  # 本地图片路径
            file_path = f'/data/one/book_data/{file_name}'  # 本地文件路径

            if await get_book_data(ttm_sql,book_name):
                continue

            print(file_url)
            print(type(file_url))
            ali.download_file(file_path, file_url)
            doc = fitz.open(file_path)
            print(doc)
            print(len(doc))  #页数
            pm = fitz.Pixmap(doc, 1)
            pm.save(cover_path)

            image_key = f'book/cover/{cover_name}'
            image_ret = await upload_image(key=image_key, localfile=cover_path)
            print(image_ret)
            print(image_ret.get('key'))
            book_ret= {}
            if i.size < 1024 * 1024 * 100:  # 大于100M 不保存七牛
                book_key = f'book/file/{file_name}'
                book_ret = await upload_image(key=book_key, localfile=file_path)
                print(book_ret)

            item = {
                'title': book_name,
                'author': '未知',
                'publish': '未知',
                'booktpye': '未知',
                'pages': len(doc),
                'down_url': file_url,
                'cover': image_ret.get('key'),
                'update_time': now(),
                'book_url': book_ret.get('key') if book_ret else '',
            }
            is_new, columns, row = Book.upsert(
                ttm_sql, Book.title == item['title'], attrs=item
            )
            if columns:
                ttm_sql.add(row)
            print(item)

    ttm_sql.commit()




