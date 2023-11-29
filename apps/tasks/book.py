
from aligo import Aligo,Auth
import fitz
from apps.tasks.celery import celery_app,BaseTask
from common.dao.book import Book
from common.libs.comm import now
from qiniu import Auth, put_file, etag
from common.helper.qiniu_helper import get_upload_token,upload_img,upload_image,upload
from common.libs.aio import run_sqlalchemy
import os


@celery_app.task(bind=True)
async def book_updata(self: BaseTask,file_id=None ):
    """
    图书信息入库
    """
    ttm_sql = self.app.ttm.get_mysql('ttm_sql')

    # auth = Auth(name='refresh_token', refresh_token='dd2e8fd6320240bbabdf2db372d7ef2a')
    ali = Aligo()

    file_id='616fb7f8d13949bc36924668883e2c3bed9fad6b'
    # 获取用户信息
    user = ali.get_user()
    if not user:
        pass
    # 获取网盘根目录文件列表
    root_file_list = ali.get_file_list()
    print(root_file_list)
    file_list = ali.get_file_list(file_id)
    print(file_list)

    @run_sqlalchemy()
    def get_book_data(db_session,title):
        return db_session.query(Book) \
            .filter(Book.title == title) \
            .first()

    for i in file_list[:100]:
        if i.size > 1024 * 1024 * 5:
            print(f'{i.name}文件{i.size // 1024 // 1024}M，跳过文件')
            continue
        print(f'{i.name} 文件{i.size // 1024 // 1024}M，开始处理文件')
        if i.type == 'file':
            file_url = i.download_url

            book_name = i.name.split('.')[0].rstrip('0123456789_')
            cover_name = book_name + '.png'
            file_name = book_name + '.pdf'
            cover_path = f'/data/one/book_data/{cover_name}'  # 本地图片路径
            file_path = f'/data/one/book_data/{file_name}'  # 本地文件路径

            if await get_book_data(ttm_sql, book_name):
                print(f'{book_name} 文件已存在，跳过....')
                continue

            ali.download_file(file_path, file_url)
            doc = fitz.open(file_path)
            pm = fitz.Pixmap(doc, 1)
            pm.save(cover_path)

            image_key = f'book/cover/{cover_name}'
            image_ret = await upload_image(key=image_key, localfile=cover_path)

            print(f'{book_name} 图片上传完成')
            print(f'{book_name} 文件上传开始')
            book_ret = {}
            if i.size < 1024 * 1024 * 10:  # 大于10M 不保存七牛
                book_key = f'book/file/{file_name}'
                book_ret = await upload_image(key=book_key, localfile=file_path)
            print(f'{book_name} 文件上传完成')

            item = {
                'title': book_name,
                'author': '未知',
                'publish': '未知',
                'booktpye': '未知',
                'pages': len(doc),
                'down_url': file_url,
                'cover': image_ret.get('key') if image_ret else '',
                'update_time': now(),
                'book_url': book_ret.get('key') if book_ret else '',
                'ali_file_id':'',
            }
            is_new, columns, row = Book.upsert(
                ttm_sql, Book.title == item['title'], attrs=item
            )
            if columns:
                ttm_sql.add(row)
            print(item)
            print(f'{book_name} 文件{i.size // 1024 // 1024}M，处理完成')
            os.remove(cover_path)
            os.remove(file_path)
            print(f'{book_name} 文件{i.size // 1024 // 1024}M，已删除本地文件')

        ttm_sql.commit()
    print('任务结束')



