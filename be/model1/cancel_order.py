#为了自动取消添加的模块
import redis
import time

#连接redis数据库
#连接池  使用连接池管理所有连接，减少每次建立、释放连接的开销
pool = redis.ConnectionPool(host='localhost',port=6379,db=0,decode_responses=True)
r=redis.StrictRedis(connection_pool=pool)

# 创建pubsub对象，该对象订阅一个频道并侦听新消息：
pubsub=r.pubsub()

#定义触发事件
def event_hander(msg):
    print('Handler',msg)
    order_id=str(msg['data'])
    print(order_id)
    # #获取订单
    # #从数据库中new_order_unpaid中找这个订单
    # order=self.session.query(New_order_unpaid).filter(New_order_unpaid.order_id=order_id)
    # #如果未找到，说明已付款，什么都不用做
    # if order.first() is None:
    #     return 200,"ok"

    # #如果能找到，就删除未支付订单
    # order.delete()
    # #添加到已删除订单中

    # #将商店中的书籍书加回去
    # detail_orders=self.session.query(New_order_detail).filter(New_order_detail.order_id=order_id)
    # # 遍历商品
    # for detail_order in detail_orders:
    #     # 获取订单中的商品数量
    #     count=detail_order.count
    #     book_id=detail_order.book_id
    #     print("count",count)
    #     # 添加回商店
    #     # 得到商店原本的数量
    #     cursor = self.session.query(Store).filter(_and(Store.book_id=book_id, Store.store_id=store_id))
    #     old_count = cursor.stock_level
    #     rowcount = cursor.update({Store.stock_level: old_count + count})
    # self.session.commit()
    # self.session.close()
    # return 200,'ok'

def auto_cancel():
    #监听过期事件，并且设置回调函数
    pubsub.psubscribe(**{'__keyevent@0__:expired':event_hander})
    while True:
        #获得事件信息，有结果就会回调函数
        message=pubsub.get_message()
        time.sleep(0.1)

#设置过期时间
# r.setex('foo',1,'bar') #10s