from sanic import Blueprint
from apps.admin_api.view import book

book_bp = Blueprint(name='数据', url_prefix='/book', strict_slashes=True)

book_bp.add_route(book.book_list, '/book_list', ['POST'], name='book_list')  #文章列表
book_bp.add_route(book.save_book, '/save_book', ['POST'], name='save_book')  #创建文章
book_bp.add_route(book.book_detali, '/book_detali/<id:int>', name='book_detali')  #查看文章
book_bp.add_route(book.delete_book, '/delete_book', ['POST'],name='delete_book')  #查看文章


