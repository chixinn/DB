# 导入库的依赖
# 只是先单纯的复制 可后台删改
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
from init_books import Book


#生成 orm 基类
#这个地方大家都要改连自己本地的
# engine = create_engine('postgresql://postgres:123456@localhost:5432/bookstore',encoding='utf-8',echo=True)
engine = create_engine('postgresql+psycopg2://chixinning:123456@localhost/bookstore',encoding='utf-8',echo=True)

# 暂时只需要跑init_database.py 

Base=declarative_base()

class SearchTitle(Base):
    __tablename__ = 'search_title'
    search_id=Column(Integer,autoincrement=True)
    title = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)

class SearchAuthor(Base):
    __tablename__ = 'search_author'
    search_id=Column(Integer,autoincrement=True)
    author = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)

class SearchBookIntro(Base):
    __tablename__ = 'search_book_intro'
    search_id=Column(Integer,autoincrement=True)
    author = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)
class SearchTags(Base):
    __tablename__ = 'search_book_tags'
    search_id=Column(Integer,autoincrement=True)
    tags = Column(Text, nullable=False,primary_key=True)
    book_id = Column(Integer, ForeignKey('book.book_id'), nullable=False)