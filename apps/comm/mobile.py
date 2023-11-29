
from aligo import Aligo,Auth




auth = Auth(name='refresh_token', refresh_token='dd2e8fd6320240bbabdf2db372d7ef2a')
ali =Aligo()

file_id='616fb7f8d13949bc36924668883e2c3bed9fad6b'
# 获取用户信息
user = ali.get_user()

# 获取网盘根目录文件列表
root_file_list = ali.get_file_list()
print( root_file_list)
file_list = ali.get_file_list(file_id)

for i in file_list:
    print(i.name)

# ttm_sql = request.app.ttm.get_mysql('ttm_sql')
#
# books = ttm_sql.query(Book).filter(Book.id.in_(book_id_list)).all()
#
# for book in books:
#     print(book.id)
#     book.delete = 1
#
