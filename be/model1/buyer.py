import sqlite3 as sqlite
import uuid
import json
import logging
import sys
sys.path.append("../")
from be.model1 import db_conn
from be.model1 import error
from datetime import datetime
import time
from init_db.init_database import Store,Users,User_store
from init_db.init_database import New_order_detail,New_order_undelivered
from init_db.init_database import New_order_unpaid
class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
   #def new_order(self, user_id, store_id, id_and_count):
    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            #uid 由'user_id'\_'store_id'_一个唯一标识符组成
            #下单成功后将uid赋值给order_id
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                # print(id_and_count)
                # print(book_id)
                # print(type(book_id))
                # print(count)
                # print(type(count))
                # # cursor = self.conn.execute(
                # #     "SELECT book_id, stock_level, book_info FROM store "
                # #     "WHERE store_id = ? AND book_id = ?;",
                # #     (store_id, book_id)

                # #不加这个转换 后面用%d select时会报错
                book_id=int(book_id)
                # print(type(book_id))
                #book = self.session.execute("SELECT  stock_level,price FROM store WHERE store_id = '%s'AND book_id = %d"%(store_id, book_id)).fetchone()
                book=self.session.query(Store).filter_by(book_id=book_id, store_id=store_id).first()
                #row = cursor.fetchone()
                if book is None:
                    return error.error_non_exist_book_id(str(book_id)) + (order_id, )

                # stock_level = book[0]
                # #print("stock_level:",stock_level)
                # price=book[1]
                stock_level = book.stock_level
                price=book.price
                # book_info = book[2]
                # book_info_json = json.loads(book_info)
                # price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(str(book_id)) + (order_id,)
                # 减库存，如果取消订单的话要加回来
                # cursor = self.conn.execute(
                #     "UPDATE store set stock_level = stock_level - ? "
                #     "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                #     (count, store_id, book_id, count))
                cursor = self.session.query(Store).filter(Store.book_id==book_id, Store.store_id==store_id, Store.stock_level >= count)
                rowcount = cursor.update({Store.stock_level: Store.stock_level - count})
                # res = self.session.execute(
                #     "UPDATE store set stock_level = stock_level - %d WHERE store_id = '%s' and book_id = %d  and stock_level >=%d" % (
                #         count, store_id, book_id, count))
                #cursor=self.session.execute()
                #if res.rowcount == 0:
                if rowcount==0:
                    return error.error_stock_level_low(str(book_id)) + (order_id, )

                # self.conn.execute(
                #         "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                #         "VALUES(?, ?, ?, ?);",
                #         (uid, book_id, count, price))
                # self.session.execute(
                #     "INSERT INTO new_order_detail(order_id, book_id, count, price) VALUES('%s',%d, %d, %d);" % (
                #         uid, book_id, count, price))
                new_order_info = New_order_detail(order_id=uid, book_id=book_id, count=count, price=price)
                self.session.add(new_order_info)
            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id))
            #记录下单时间
            timenow =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #将新订单加入待付款
            # self.session.execute(
            #         "INSERT INTO new_order_unpaid(order_id, store_id, buyer_id,price,commit_time) VALUES('%s','%s','%s',%d,'%s');" % (
            #             uid, store_id, user_id,price,timenow))
            new_order_unpaid = New_order_unpaid(order_id=uid, store_id=store_id,buyer_id=user_id,price=price,commit_time=timenow)
            self.session.add(new_order_unpaid)
            self.session.commit()
            self.session.close()
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        #conn = self.conn
        try:
            # cursor = conn.execute("SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?", (order_id,))
            # row = cursor.fetchone()
            #待支付中是否有该用户该订单
            # row = self.session.execute(
            # "SELECT buyer_id,price,store_id FROM new_order_unpaid WHERE order_id = '%s'" % (order_id)).fetchone()
            row=self.session.query(New_order_unpaid).filter_by(order_id=order_id).first()
            print(row)
            if row is None:
                return error.error_invalid_order_id(order_id)

            
            # buyer_id = row[0]
            # price=row[1]
            # store_id = row[2]
            buyer_id=row.buyer_id
            price=row.price
            store_id=row.store_id

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # cursor = conn.execute("SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,))
            # row = cursor.fetchone()
            # 检查密码 余额
            # row = self.session.execute(
            # "SELECT balance, password FROM usr WHERE user_id = '%s';" % (buyer_id)).fetchone()
            row=self.session.query(Users).filter_by(user_id=buyer_id).first()
            
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            check_password=row.password
            balance=row.balance
            #balance = row[0]
            #if password != row[1]:
            if password !=check_password:
                return error.error_authorization_fail()
            #记录卖家id
            # cursor = self.session.execute("SELECT store_id, user_id FROM user_store WHERE store_id = '%s';"%(store_id))
            # row = cursor.fetchone()
            row=self.session.query(User_store).filter_by(store_id=store_id).first()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            #seller_id = row[1]
            seller_id=row.user_id

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            #cursor = self.session.execute("SELECT book_id, count, price FROM new_order_detail WHERE order_id = '%s';"%(order_id))
            cursor = self.session.query(New_order_detail).filter_by(order_id=order_id)
            total_price = 0
            for row in cursor.all():
                count = row.count
                price = row.price
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            #买家支付 余额扣钱
            #cursor = self.session.execute("UPDATE usr set balance = balance - %d WHERE user_id = '%s' AND balance >= %d"%(total_price, buyer_id, total_price))
            cursor = self.session.query(Users).filter(Users.user_id==buyer_id, Users.balance>=total_price)
            rowcount = cursor.update({Users.balance: Users.balance - total_price})
            if rowcount == 0:
                return error.error_not_sufficient_funds(order_id)
            #卖家加钱
            #cursor = self.session.execute("UPDATE usr set balance = balance + %d WHERE user_id = '%s'"%(total_price, seller_id))
            cursor = self.session.query(Users).filter(Users.user_id==seller_id)
            rowcount = cursor.update({Users.balance: Users.balance + total_price})
            if rowcount == 0:
                return error.error_non_exist_user_id(seller_id)
            # 删除待付订单
            #cursor = self.session.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s';"% (order_id ))
            
            query = self.session.query(New_order_unpaid).filter(New_order_unpaid.order_id == order_id)
            query.delete()
            print("*****")
            rowcount=query.first()
            #print(cursor.rowcount)
            #if cursor.rowcount == 0:
            if rowcount==0:
                return error.error_invalid_order_id(order_id)
            #删除订单的详细信息
            #还未发货暂不删除订单详细信息
            # cursor = self.session.execute("DELETE FROM new_order_detail where order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            
            #在待发货中加入该订单
            timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("******")
            new_orde = New_order_undelivered(
                order_id=order_id,
                buyer_id = buyer_id ,
                store_id=store_id,
                price=price,
                purchase_time=timenow
            )
            self.session.add(new_orde)
            # re=self.session.execute(
            # "INSERT INTO new_order_undelivered(order_id, buyer_id,store_id,price,purchase_time) VALUES('%s', '%s','%s',%d,'%s');" % (
            #     order_id, buyer_id, store_id, price,timenow))
            # print(re.rowcount)
            #self.session.commit()
            self.session.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
#买家充值
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            usr = self.session.query(Users).filter_by(user_id=user_id).first()
            #usr = self.session.execute("SELECT password  from usr where user_id= '%s'"%(user_id,)).fetchone()
            #row = cursor.fetchone()
            if usr is None:
                return error.error_authorization_fail()

            if usr.password != password:
                return error.error_authorization_fail()
            cursor = self.session.query(Users).filter(Users.user_id==user_id)
            rowcount = cursor.update({Users.balance: Users.balance + add_value})
            # cursor = self.session.execute(
            #     "UPDATE usr SET balance = balance + %d WHERE user_id = '%s'"%
            #     (add_value, user_id))
            
            #if cursor.rowcount == 0:
            if rowcount==0:
                return error.error_non_exist_user_id(user_id)

            self.session.commit()
            self.session.close()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    # 买家查询 
    # 比较索引 和模糊查询的 检索效率
    # 最后这两个接口是要删一个的
    def search_book_author_like(self,store_id:str,search_type:str,search_input:str)->(int, [dict]):
        time1=time.time()
        res=[]
        resglobal=[]
        # 下面这种模糊查询的方式是不好用的
        rows=self.session.execute("SELECT DISTINCT book_id FROM search_author WHERE tsv_column @@ '%s'"%(search_input)).fetchall()
        print("SELECT book_id FROM search_author WHERE tsv_column @@ '%s'"%(search_input))
        # rows=self.session.execute("SELECT book_id from search_author where author like '%s' order by search_id" % ('%'+search_input+'%')).fetchall()
        if len(rows)!=0:
            for row in rows:
                restmp={}
                book_global_id=row[0]#?
                ans=self.session.execute("SELECT author,title,book_intro,original_price from book where book_id ='%s' " % (book_global_id)).fetchone()
                restmp['book_id']=book_global_id
                restmp['author']=ans[0]
                restmp['title']=ans[1]
                restmp['book_intro']=ans[2]
                restmp['price']=ans[3]
                resglobal.append(restmp) 
        else:
            restmp={}
            restmp['error_code[597]']="书库里找不到这个结果"
            res.append(restmp)
            return 597,res
        if search_type=='global':
            #需要加图再加图
            time2=time.time()
            timetmp={}
            timetmp['time complexity res']=time2-time1
            resglobal.insert(0,timetmp)   
            return 200,resglobal
        elif search_type=='instore': # 待DEBUG
            # 首先获取该店的图书信息
            # 先要加store id不对的边缘检测?
            rows_likely_in_store=self.session.execute(
                "SELECT DISTINCT book_id,title,author,book_intro from book where book.book_id in (SELECT DISTINCT book_id FROM search_author WHERE tsv_column @@ '%s');"% (search_input)
                ).fetchall()
            print(  "SELECT DISTINCT book_id,title,author,book_intro from book where book.book_id in (SELECT DISTINCT book_id FROM search_author WHERE tsv_column @@ '%s');"% (search_input))
            if len(rows_likely_in_store)!=0:
                for row in rows_likely_in_store:
                    book_instore_id=row[0]#先获取book_id，毕竟一个书店有的书和全局有的书数据量相比还是小的
                    restmp={}
                    ans=self.session.execute("SELECT stock_level,price FROM store where store_id = '%s' and book_id = '%s'"%(store_id,book_instore_id)).fetchone()
                    if ans ==None:
                        # 测试用
                        # restmp={}
                        # restmp['error_code[599]']="这本没有哦!"
                        # res.append(restmp)
                        continue
                    else:
                        print("SELECT stock_level,price FROM store where store_id = '%s' and book_id = '%s'"%(store_id,book_instore_id))
                        stock=ans[0]
                        current_price=[1]
                        restmp['book_id']=row[0]
                        restmp['author']=row[2]
                        restmp['title']=row[1]
                        restmp['book_intro']=row[3]
                        restmp['current_price']=current_price
                        restmp['stock_level']=stock
                        restmp['store_id']=store_id
                        res.append(restmp)
                #根据book_id和字典确定author的搜索结果。
                time2=time.time()
                timetmp={}
                timetmp['time complexity res']=time2-time1
                res.insert(0,timetmp)
                if(len(res)==1):
                    restmp={}
                    restmp['error_code[598]']="本店一本也没有！"
                    res.append(restmp)
                    return 598,res
                return 200,res
            else:
                restmp={}
                restmp['error_code[599]']="书库和本店一本也没有！"
                res.append(restmp)
                return 599,res
    

    def search_functions(self,store_id:str,search_type:str,search_input:str,field:str)->(int, [dict]):
        time1=time.time()
        res=[]
        resglobal=[]
        # 下面这种模糊查询的方式是不好用的
        rows=self.session.execute("SELECT DISTINCT book_id FROM %s WHERE tsv_column @@ '%s'"%(field,search_input)).fetchall()
        print("SELECT book_id FROM %s WHERE tsv_column @@ '%s'"%(field,search_input))
        # rows=self.session.execute("SELECT book_id from search_author where author like '%s' order by search_id" % ('%'+search_input+'%')).fetchall()
        if len(rows)!=0:
            for row in rows:
                restmp={}
                book_global_id=row[0]#?
                ans=self.session.execute("SELECT author,title,book_intro,original_price,tags from book where book_id ='%s' " % (book_global_id)).fetchone()
                restmp['book_id']=book_global_id
                restmp['author']=ans[0]
                restmp['title']=ans[1]
                restmp['book_intro']=ans[2]
                restmp['price']=ans[3]
                restmp['tags']=ans[4]
                resglobal.append(restmp) 
        else:
            restmp={}
            restmp['error_code[597]']="书库里找不到这个结果"
            res.append(restmp)
            return 599,res
        if search_type=='global':
            #需要加图再加图
            time2=time.time()
            timetmp={}
            timetmp['time complexity res']=time2-time1
            resglobal.insert(0,timetmp)   
            return 200,resglobal
        elif search_type=='instore': # 待DEBUG(应该是好的)
            # 首先获取该店的图书信息
            # 先要加store id不对的边缘检测?
            rows_likely_in_store=self.session.execute(
                "SELECT DISTINCT book_id,title,author,book_intro,tags from book where book.book_id in (SELECT DISTINCT book_id FROM %s WHERE tsv_column @@ '%s');"% (field,search_input)
                ).fetchall()
            # print(  "SELECT DISTINCT book_id,title,author,book_intro from book where book.book_id in (SELECT DISTINCT book_id FROM search_author WHERE tsv_column @@ '%s');"% (search_input))
            if len(rows_likely_in_store)!=0:
                for row in rows_likely_in_store:
                    book_instore_id=row[0]#先获取book_id，毕竟一个书店有的书和全局有的书数据量相比还是小的
                    restmp={}
                    ans=self.session.execute("SELECT stock_level,price FROM store where store_id = '%s' and book_id = '%s'"%(store_id,book_instore_id)).fetchone()
                    if ans ==None:
                        # 测试用
                        # restmp={}
                        # restmp['error_code[599]']="这本没有哦!"
                        # res.append(restmp)
                        continue
                    else:
                        print("SELECT stock_level,price FROM store where store_id = '%s' and book_id = '%s'"%(store_id,book_instore_id))
                        stock=ans[0]
                        current_price=[1]
                        restmp['book_id']=row[0]
                        restmp['author']=row[2]
                        restmp['title']=row[1]
                        restmp['book_intro']=row[3]
                        restmp['book_tags']=row[3]
                        restmp['current_price']=current_price
                        restmp['stock_level']=stock
                        restmp['store_id']=store_id
                        res.append(restmp)
                #根据book_id和字典确定author的搜索结果。
                time2=time.time()
                timetmp={}
                timetmp['time complexity res']=time2-time1
                res.insert(0,timetmp)
                if(len(res)==1):
                    restmp={}
                    restmp['error_code[598]']="本店一本也没有！"
                    res.append(restmp)
                    return 599,res
                return 200,res
            else:
                restmp={}
                restmp['error_code[599]']="书库和本店一本也没有！"
                res.append(restmp)
                return 599,res
    
