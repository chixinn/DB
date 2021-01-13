import pytest
import uuid
# from fe.access.new_buyer import register_new_buyer
from fe.access import buyer
from fe import conf
import uuid
import random
import time
from fe.access.new_buyer import register_new_buyer

# todo 编更多的case提高效率
class TestSearchAuthor:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_search_{}".format(str(uuid.uuid1()))
        self.password = self.user_id
        self.buyer = register_new_buyer(self.user_id, self.password)
        self.search_type_global="global"
        self.search_type_instore="instore"
        self.author_in='杨红'
        self.author_out='英'
        self.tag_in='美丽'
        self.tag_in_='流浪记'
        self.author_not_in='芥见下下'
        self.author_field='search_author'
        self.title_field='search_title'
        self.tags_field='search_book_tags'
        self.book_intro_field='search_book_intro'
        yield
   
    def test_global_ok(self):
        code=self.buyer.search_functions("1",self.search_type_global,self.tag_in,self.book_intro_field)[0]
        assert code == 200 
    def test_instore_ok(self):
        code=self.buyer.search_functions("1",self.search_type_instore,self.tag_in_,self.book_intro_field)[0]
        assert code == 200 
    # store_id就不对
    def test_store_id_err(self):
        code=self.buyer.search_functions("9998",self.search_type_instore,self.author_not_in,self.book_intro_field)[0]
        assert code == 599
    # book表就没有该作者：本店搜索
    def test_no_such_author_err2(self):
        code=self.buyer.search_functions("9999",self.search_type_global,self.author_out,self.book_intro_field)[0]
        assert code == 599
    # book表有该作者，但我们店没有
    def test_no_such_author_instore_err(self):
        code=self.buyer.search_functions("1",self.search_type_instore,self.author_out,self.book_intro_field)[0]
        assert code == 599#
    
