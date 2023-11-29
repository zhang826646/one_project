
from aligo import Aligo,Auth
import fitz
from celery_start import celery_app
from common.dao.book import Book
from common.libs.comm import now
from qiniu import Auth, put_file, etag
from common.helper.qiniu_helper import get_upload_token,upload_img,upload_image,upload


@celery_app.task(bind=True, acks_late=True)
async def book_updata(self: BaseTask,file_id=None ):
    """
    图书信息入库
    """
    token = await get_upload_token('books', False, size=1000)
    ttm_sql = self.app.ttm.get_mysql('ttm_sql')

    auth = Auth(name='refresh_token', refresh_token='dd2e8fd6320240bbabdf2db372d7ef2a')
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
    book_objs=[]
    for i in file_list[:2]:
        if i.type=='file':
            file_url=i.download_url

            # if i.size > 1024 * 1024 * 10:  # 大于10M 文件不保存七牛
            #     continue
            # if i.size > 1024 * 1024 * 100:  # 大于100M 文件不读取详细数据
            #     continue

            file_name=i.name
            tu_name=file_name.split('.')[0]+'.png'
            file_path=f'/data/one/book_data/{file_name}'
            print(file_url)
            print(type(file_url))
            ali.download_file(file_path, file_url)
            doc = fitz.open(file_path)
            print(doc)
            print(len(doc))  #页数
            # nums = doc._getXrefString(1)
            # print(nums)
            # trans = fitz.Matrix(0, 0).preRotate(0)
            # pm = doc[1].getPixmap(matrix=trans, alpha=False)
            # print(pm)
            pm = fitz.Pixmap(doc, 1)
            pm.save(f'/data/one/book_data/{tu_name}')
            image_key = upload_image(data=pm, path='book/image')
            book_key = upload(data=doc, path='book')
            book = Book()
            book.title = file_name.split('.')[0]
            book.booktpye = '未知'
            book.pages = len(doc)
            book.book_url = file_url
            book.cover = 'book/imageimage/key'
            book.update_time = now()
            book_objs.append(book)

    ttm_sql.bulk_save_objects(book_objs)




