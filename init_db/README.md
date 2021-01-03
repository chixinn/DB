# 2020.12.20更新(cxn)

cxn: 第一轮初始化数据库，添加了一些样例/用户和一点书(书的信息是我自己插进去的，等会再研究怎么把所有书的数据按照助教学长的格式读入进去) <br>

## 运行方式：
### 先要把把本地数据库连接的用户名和密码改了
就是下面这个地方<br>
engine = create_engine('postgresql+psycopg2://chixinning:123456@localhost/bookstore',encoding='utf-8',echo=True)<br>
cd 进be/init_db/文件夹, `python init_database.py'
## 亟待解决的问题
1. user_id和username还留不留，我写成user_id=user_Login_account,就类似于我们日常用的淘宝用户名和注册邮箱
2. 书的详细信息存储表格的设计
3. git协作和咋设成私有仓库的还没太学会Orz

# 2021.1.2更新(cxn)
图书基本schema与助教数据集中schema保持一致
将图片BLOB数据分离另新建表：
> 原要求2.核心数据使用关系型数据库（PostgreSQL或MySQL数据库）。 blob数据（如图片和大段的文字描述）可以分离出来存其它NoSQL数据库或文件系统。

# 2021.1.3更新(cxn)
 初始化数据库执行 init_database.py
 最终的book-schema
class BookWhole(Base):
    # PostgreSQL提供text类型， 它可以存储任何长度的字符串。
    __tablename__ = 'book'
    book_id = Column(Integer, primary_key=True,autoincrement=True)#自增
    title = Column(Text, nullable=False)
    author = Column(Text,nullable=True)
    publisher = Column(Text,nullable=True)
    original_title = Column(Text,nullable=True)
    translator = Column(Text,nullable=True)
    pub_year = Column(Text,nullable=True)
    pages = Column(Integer,nullable=True)
    price = Column(Integer,nullable=True)  
    binding = Column(Text,nullable=True)
    isbn = Column(Text,nullable=True)
    author_intro = Column(Text,nullable=True)
    book_intro = Column(Text,nullable=True)
    content = Column(Text,nullable=True)
    tags = Column(Text,nullable=True)

> 先执行init_database.py，再执行book.py    
> 如果遇到报错，unable to opendatabase file,是执行文件的路径的问题，需要在DB这个目录下执行 `python init_db/book.py`而不是在 init_db这个目录下执行`python book.py`不然就会报错！！！！

图片另建新表跟检索有关
所有价格都是分：原爬下来的没单位我也默认成分了。
如果遇到报错 可能需要执行drop table book cascade;
图书库的数据量可以在book.py下的`init_postgresql(self,start,size)`里面更改，通过参数更改数量。
豆瓣3G多的数据暂时没有放进来，所以fe/data/book.db和fe/data/book_lx.db是一样的，太大了，git不方便
用Navicat可以打开book.db文件，看看里面数据长啥样子可以从这里