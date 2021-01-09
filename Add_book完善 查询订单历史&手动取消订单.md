### Add_book完善 查询订单历史&手动取消订单

wwq

1.添加查询订单历史功能 测试通过

测试用例

- Test_ok 测试正常情况 （测试能否正确查到未付款、已付款未发货、已发货未收货、已收货的历史订单信息）
- 测试用户不存在
- 测试用户没有购买记录

2.添加手动取消订单功能 测试通过

测试用例

- 已付款未发货
- 未付款
- User_id不存在
- 已发货

3.add_book完善

调整函数接口 传price 将用户定义的售价传入store中

1）修改be/view1/seller.py

def seller_add_book():

```python
code, message = s.add_book(user_id, store_id, book_info.get("id"),book_info.get("price"), json.dumps(book_info), stock_level)
```

传入用户输入的价格

2）修改be/model1/seller.py

```python
def add_book(self, user_id: str, store_id: str, book_id: str,price:int, book_json_str: str, stock_level: int):
```

```python
            store=Store()
            store.book_id=int(book_id)
            store.store_id=store_id
            store.stock_level=stock_level
            ###这里需改动 函数接口中增加price 这里为用户输入的价格 不是书的零售价 目前不影响测试
            #store.price=book['price']
            store.price=price
            self.session.add(store)
```

