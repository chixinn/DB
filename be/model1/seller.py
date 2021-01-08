import sqlite3 as sqlite
import sys
sys.path.append("../")
from be.model1 import error
from be.model1 import db_conn
import json

class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            
            if not self.user_id_exist(user_id):
                print(user_id)
                return error.error_non_exist_user_id(user_id)
            
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            # print("*******")
            book = json.loads(book_json_str)
            # print(book)
            # print("******",type(book))
            #这里的tag是list型的 数据库定义的是text型 但是可以正常插入 如果查找书籍时出现问题 在此修改
            # thelist = []  # 由于没有列表类型，故使用将列表转为text的办法
            # for tag in book.get('tags'):
            #     if tag.strip() != "":
            #             # book.tags.append(tag)
            #         thelist.append(tag)
            # book['tags'] = str(thelist)  # 解析成list请使用eval(
            #如果图书要插入图片 后期在此处更改
            #插入bookinfo
            # print('tags',book['tags'])
            # print("type of tag:",type(book['tags']))
            # print("type of binding:",type(book['binding']))
            #print("type of currency unit:",type(book['currency_unit']))
            ############
            #由于助教给的body里没有currency_unit所以这里没有加入该值
            #如需后期加入 在insert 中更改即可
            # print("bookprice",book['price'])
            ##重要！！！！！
            #判断书是否已经加在书里
            row = self.session.execute("SELECT book_id FROM book WHERE book_id = '%s';" % (book_id,)).fetchone()
            if row is None:
                book = json.loads(book_json_str)
                thelist = []  # 由于没有列表类型，故使用将列表转为text的办法
                for tag in book.get('tags'):
                    if tag.strip() != "":
                        # book.tags.append(tag)
                        thelist.append(tag)
                book['tags'] = str(thelist) 
                self.session.execute(
                        "INSERT into book( book_id, title,author,publisher,original_title,translator,"
                        "pub_year,pages,original_price,binding,isbn,author_intro,book_intro,"
                        "content,tags) VALUES ( :book_id, :title,:author,:publisher,:original_title,:translator,"
                        ":pub_year,:pages,:original_price,:binding,:isbn,:author_intro,:book_intro,"
                        ":content,:tags)",
                        {'book_id': book['id'], 'title': book['title'], 'author': book['author'],
                         'publisher': book['publisher'], 'original_title': book['original_title'],
                         'translator': book['translator'],
                         'pub_year': book['pub_year'], 'pages': book['pages'], 'original_price': book['price'],
                         
                         'binding': book['binding'], 'isbn': book['isbn'], 'author_intro': book['author_intro'],
                         'book_intro': book['book_intro'],
                         'content': book['content'], 'tags': book['tags']})
                print("book info success")
            self.session.execute("INSERT into store(store_id, book_id,  stock_level,price) VALUES ('%s', %d,  %d,%d)"%(store_id, int(book_id),  stock_level,book['price']))
            self.session.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            self.session.execute("UPDATE store SET stock_level = stock_level + %d "
                                 "WHERE store_id = '%s' AND book_id = %d" % (add_stock_level, store_id, int(book_id)))
            self.session.commit()
            
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.session.execute("INSERT into user_store(store_id, user_id) VALUES ('%s', '%s')"% (store_id, user_id))
            self.session.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
