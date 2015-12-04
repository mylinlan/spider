# -*- coding:utf-8 -*-

import os
import time
import datetime
import re
import requests
import mysql
from bs4 import BeautifulSoup
from pybloomfilter import BloomFilter


class MySpider(object):
    def __init__(self, start_url, basic_url):
        self.basic_url = basic_url
        self.start_url = start_url
        self.mysql = mysql.Mysql()
        self.re = re
        self.time = time
        self.datetime = datetime
        self.requests = requests

        # 使用bloom_filter去重，每次从文件中读取dump.bloom
        if os.path.isfile('filter.bloom'):
            self.bf = BloomFilter.open('filter.bloom')
        else:
            self.bf = BloomFilter(10000000, 0.01, 'filter.bloom')

    def __get_time(self):
        return self.datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __cal_time(self, date1, date2):
        date1 = self.time.strptime(date1, "%Y-%m-%d %H:%M:%S")
        date2 = self.time.strptime(date2, "%Y-%m-%d %H:%M:%S")
        date1 = self.datetime.datetime(date1[0], date1[1], date1[2], date1[3], date1[4], date1[5])
        date2 = self.datetime.datetime(date2[0], date2[1], date2[2], date2[3], date2[4], date2[5])
        return str(date2 - date1)

    def __log(self, log_str, *args, **kw):
        current_time = self.__get_time()
        print current_time + ' : ' + log_str,
        for each in args:
            print each,
        print '\n',
        for each in kw.keys():
            print current_time + ' : ' + each + ' is ' + kw[each]

    def __process_text(self, my_str):
        my_str = self.re.sub("http.*?html", "", my_str).encode('utf-8')
        if type(my_str) == 'unicode':
            my_str = my_str.encode('utf-8')
        return my_str.replace(" ", "").replace("　　", "").replace('\n', '')

    def __open_url(self, url):
        req = self.requests.get(url)
        content = req.text
        soup = BeautifulSoup(content)
        return soup

    def __process_sub_content(self, result, insert_id):
        for each in result:
            # print '\n' + '楼层：'
            # 时间以及作者
            # print each.attrs.get('js_restime')
            # print each.a.text
            # 内容
            # bbs_content = each.select("[class~=bbs-content]")
            # text = bbs_content[0].text.strip()
            # 去除链接以及空格
            # text = re.sub("http.*?html", "", text).encode('utf-8')
            # text = text.replace(" ", "").replace("　　", "")
            # print self.__process_text(text)
            # print process_text(text)
            replies = each.select('ul li')
            for reply in replies:
                self.__log('process the reply ... start')
                reply_time = reply.get('_replytime')
                reply_author = reply.get('_username')
                reply_content = reply.select("[class~=ir-content]")
                reply_text = reply_content[0].text
                reply_dict = {
                    "title_id": insert_id,
                    "author": reply_author,
                    "time": reply_time,
                    "text": reply_text
                        }
                self.__log('content is', reply_text)
                self.__log('insert to database ...start')
                self.mysql.insert_data('reply', reply_dict)
                self.__log('insert to database ...done')
                self.__log('process the reply ... done')
        # 处理每一层楼

    def process_content_page(self, url, author, reply_time, insert_id):
        self.__process_reply_page(url, author, reply_time, insert_id)

    def __process_reply_page(self, url, author, reply_time, insert_id):
        self.__log('process reply page... start')
        soup = self.__open_url(url)
        # 各层楼的tag
        result = soup.select("[class~=atl-item]")

        if len(result):
            self.__log('the html was read successfully')
        else:
            self.__log('html read fail. maybe the page is lose. function return')
            self.__log('process reply page ... done')
            return
        # 回复页总页数
        page_id = soup.select("form a")
        if page_id:
            total_page_num = int(page_id[-2].text)
        else:
            total_page_num = 1

        self.__log('have read', total_page_num, 'pages')

        # 首层楼的内容
        main_content = result[0].select("[class~=bbs-content]")
        main_content = main_content[0].text.strip()
        main_text = self.__process_text(main_content)
        reply_dict = {
                    "title_id": insert_id,
                    "author": author,
                    "time": reply_time,
                    "text": main_text
                    }
        self.mysql.insert_data('reply', reply_dict)
        result = result[1:]
        self.__log('process every floor')
        self.__process_sub_content(result, '1')
        if total_page_num > 1:
            for num in range(2, total_page_num + 1):
                self.__log('process the', str(num), 'reply page ... start')
                next_url = url[:-7]+str(num)+url[-6:]
                print next_url
                new_soup = self.__open_url(next_url)
                result = new_soup.select("[class~=atl-item]")
                self.__process_sub_content(result, insert_id)
                self.__log('process the', str(num), 'reply page ... done')
        self.__log('process reply page ... done')

    def __process_titles_page(self, page_url):
        self.__log('reading titles page .... start')
        req = self.requests.get(page_url)
        content = req.text
        soup = BeautifulSoup(content)

        # 获取所有标题
        titles = soup.select('tbody tr')
        # 去掉不符合的部分
        titles = titles[1:]
        # 对每一个标题进行处理
        self.__log('reading titles page .... done')
        self.__log('processing all titles in', self.start_url, ' ... start')
        counter = 1
        for each in titles:
            # 获取标题的tag信息
            # 注意在beautifulSoup的tag中，空白也是标签，即相邻两个td之间标签还有空白
            # 所以下面content索引需要考虑到这点
            self.__log('process the', counter, 'title', ' ... start')
            counter += 1
            title_content = each.contents
            title_href = title_content[1].a.get('href')         # 获取标题链接
            title_text = title_content[1].text.strip()          # 获取标题内容
            title_author = title_content[3].a.text              # 获取作者
            title_click_num = title_content[5].text             # 点击数
            title_reply_number = title_content[7].text          # 获取回复数
            title_time = title_content[9].get('title')          # 获取时间
            sub_href = self.basic_url + title_href                   # 子链接
            # 构造标题的字典,插入标题
            title_dict = {
                "reply_num": title_reply_number,
                "click_num": title_click_num,
                "author": title_author,
                "time": title_time,
                "link": sub_href,
                "text": title_text
                    }
            # for each in title_dict:
            #    print each
            #    print type(title_dict[each])
            # 利用链接地址和回复数判断是否重复
            # flag = sub_href + title_click_num
            flag = sub_href
            if not (self.bf.add(flag)):
                self.__log('', flag, 'not in bloom filter')
                self.__log('insert to database ... start')

                insert_id = self.mysql.insert_data("titles", title_dict)
                self.__log('insert to database ... done')
                self.__process_reply_page(sub_href, title_author.encode('utf-8'), title_time, str(insert_id))
            self.__log('process the', counter, 'title', ' ... done')

        # 下一页的链接
        next_page_tag = soup.find('a', text='下一页')
        if next_page_tag:
            next_page = next_page_tag.get('href')
            next_page = self.basic_url + next_page
        else:
            next_page = None
        return next_page

    # 清空bloom filter
    def clean_bloom_filter(self):
        self.__log('clean all in bloom filter ... start')
        self.bf.clear_all()
        self.__log('clean all in bloom filter ... done')

    def bloom_filter_len(self):
        return len(self.bf)

    def main(self):
        self.__log('spider ... start')
        self.__log('process start url ... running')
        next_page = self.__process_titles_page(self.start_url)
        self.__log('process start url ... done')
        start_time = self.__get_time()
        print start_time
        depth = 1
        while next_page:
            # if depth == 2:
            #    break
            self.__log('now it is the', str(depth), 'page')
            next_page = self.__process_titles_page(next_page)
            depth += 1
        end_time = self.__get_time()
        print end_time
        duration = self.__cal_time(start_time, end_time)
        self.__log('duration are', duration)
        self.__log('spider ... done')

    def clean_table(self, table):
        self.mysql.clean_table(table)

    def test(self):
        test_url = 'http://bbs.tianya.cn/post-333-778768-1.shtml'
        print self.bf.add(test_url)

my_url = 'http://bbs.tianya.cn/list-287-1.shtml'
my_basic_url = 'http://bbs.tianya.cn'
spider = MySpider(my_url, my_basic_url)

# spider.clean_bloom_filter()
spider.main()
# spider.clean_table('reply')
# spider.test()
# print spider.bloom_filter_len()
# my_test_url = 'http://bbs.tianya.cn/post-333-537595-1.shtml'
# spider.process_content_page(my_test_url, 'lin', '2015-12-2 22:40:00', '1')


