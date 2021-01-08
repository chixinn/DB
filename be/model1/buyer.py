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
from init_db.init_database import Store
from init_db.init_database import New_order_detail
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
            row = self.session.execute(
            "SELECT buyer_id,price,store_id FROM new_order_unpaid WHERE order_id = '%s'" % (order_id)).fetchone()
            print(row)
            if row is None:
                return error.error_invalid_order_id(order_id)

            #order_id = row[0]
            buyer_id = row[0]
            price=row[1]
            store_id = row[2]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # cursor = conn.execute("SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,))
            # row = cursor.fetchone()
            # 检查密码 余额
            row = self.session.execute(
            "SELECT balance, password FROM usr WHERE user_id = '%s';" % (buyer_id)).fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()
            #记录卖家id
            cursor = self.session.execute("SELECT store_id, user_id FROM user_store WHERE store_id = '%s';"%(store_id))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor = self.session.execute("SELECT book_id, count, price FROM new_order_detail WHERE order_id = '%s';"%(order_id))
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            #买家支付 余额扣钱
            cursor = self.session.execute("UPDATE usr set balance = balance - %d WHERE user_id = '%s' AND balance >= %d"%(total_price, buyer_id, total_price))
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)
            #卖家加钱
            cursor = self.session.execute("UPDATE usr set balance = balance + %d WHERE user_id = '%s'"%(total_price, seller_id))

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(seller_id)
            # 删除待付订单
            cursor = self.session.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s';"% (order_id ))
            print("*****")
            print(cursor.rowcount)
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)
            #删除订单的详细信息
            #还未发货暂不删除订单详细信息
            # cursor = self.session.execute("DELETE FROM new_order_detail where order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            
            #在待发货中加入该订单
            timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("******")
            re=self.session.execute(
            "INSERT INTO new_order_undelivered(order_id, buyer_id,store_id,price,purchase_time) VALUES('%s', '%s','%s',%d,'%s');" % (
                order_id, buyer_id, store_id, price,timenow))
            print(re.rowcount)
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
            usr = self.session.execute("SELECT password  from usr where user_id= '%s'"%(user_id,)).fetchone()
            #row = cursor.fetchone()
            if usr is None:
                return error.error_authorization_fail()

            if usr[0] != password:
                return error.error_authorization_fail()

            cursor = self.session.execute(
                "UPDATE usr SET balance = balance + %d WHERE user_id = '%s'"%
                (add_value, user_id))
            
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.session.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
