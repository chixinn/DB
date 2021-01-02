import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String #区分大小写
from sqlalchemy import create_engine, PrimaryKeyConstraint,Float
from sqlalchemy.ext.declarative import declarative_base
# 创建表中的字段(列)
from sqlalchemy import Column
# 表中字段的属性
from sqlalchemy import Integer, String, ForeignKey,Text,LargeBinary,DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime


'''class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []'''


engine = create_engine('postgresql+psycopg2://chixinning:123456@localhost/bookstore',encoding='utf-8',echo=True)
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()

class Book(Base):
    __tablename__ = 'book_whole'
    book_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    price=Column(Integer)#货币单位是分 所以价格类型是整数
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    picture_id = Column(String(500),ForeignKey("book_images.picture_id"))

#关于图片或者文件在数据库的存储方式归纳:https://cloud.tencent.com/developer/article/1343468

class BookImages(Base):
    __tablename__ = 'book_images'#postgresql天生不区分大小写
    picture_id = Column(String(500), primary_key=True)
    book_id = Column(Integer, ForeignKey("book_whole.book_id"))
    picture_url = Column(String(500)) # 图片命名：userId + 上传时间戳

def init_books():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    #先drop再create
    # Base.metadata.drop_all(engine) 不能连续drop两次
    Base.metadata.create_all(engine)
    # 提交即保存到数据库
    session.commit()
    # 关闭session
    session.close()

class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "data/book.db")
        self.db_l = os.path.join(parent_path, "data/book_lx.db")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

    def get_book_count(self):
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT count(id) FROM book")
        row = cursor.fetchone()
        return row[0]

    def get_book_info(self, start, size) -> [Book]:
        books = []
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (size, start))
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]

            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            picture = row[16]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode('utf-8')
                    book.pictures.append(encode_str)
            books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books


if __name__ == '__main__':

    bookdb=BookDB(large=False)#导入整张表 43988数据 还没跑通 不知道多进程会不会比单进程快

    init_books()
   