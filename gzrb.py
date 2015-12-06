#!/usr/bin/env python
# encoding: utf-8

import os
import time
import datetime
import re
import requests
import mysql
from bs4 import BeautifulSoup
from pybloomfilter import BloomFilter


class MySpider(object):
    def __init__(self):
        self.mysql = mysql.Mysql()
        self.re = re
        self.time = time
        self.datetime = datetime
        self.requests = requests

        # 使用bloom_filter去重，每次从文件中读取dump.bloom
        if os.path.isfile('new_filter.bloom'):
            self.bf = BloomFilter.open('new_filter.bloom')
        else:
            self.bf = BloomFilter(10000000, 0.01, 'new_filter.bloom')

    def __process_text(self, my_str):
        my_str = self.re.sub("http.*?html", "", my_str).encode('utf-8')
        if type(my_str) == 'unicode':
            my_str = my_str.encode('utf-8')
        return my_str.replace(" ", "").replace("　　", "").replace('\n', '')

    def open_url(self, url):
        html = self.requests.get(url)
        code = html.encoding
        # print code
        content = html.content.decode(code, 'ignore')
        soup = BeautifulSoup(content)
        return soup

    def process_content_page(self, url):
        soup = self.open_url(url)
        body = soup.find_all("p")
        # print soup.contents
        content = ''
        for each in body:
            content += each.text.strip()
            # print each.text.strip()
        return self.__process_text(content)

    def process_title_page(self, url):
        soup = self.open_url(url)
        result = soup.find("table", class_="mt12 p14")
        titles = result.find_all('tr')
        titles = titles[1:-1]
        # 处理每个标题
        for each in titles:
            title_href = each.a.get('href')
            if not self.bf.add(title_href):
                text = each.text.strip()
                title_time = '20' + text[-14:] + ':00'
                content = text[1:-15].strip()
                print title_time + '\n' + content + '\n' + title_href
                title_text = self.process_content_page(title_href)

                # 构造插入字典
                title_dict = {
                    'link': title_href,
                    'title': content,
                    'text': title_text.decode('utf-8', 'ignore'),
                    'time': title_time
                }
                # 插入数据库
                self.mysql.insert_data('gzrb_titles', title_dict)

        # 得到下一页
        result = soup.find("table", class_="mt12 p12")
        result = result.find_all('a')
        if len(result) == 1:
            next_page_href = result[0].get('href')
            # print result[0].text
        elif len(result) == 2:
            next_page_href = result[1].get('href')
            # print result[1].text
        else:
            next_page_href = None
        # print next_page_href
        return next_page_href

    def clean_bloom_filter(self):
        self.bf.clear_all()

    def process_nav(self, url):
        # 对于每个标题页，如果有下一页，则继续迭代
        next_page = self.process_title_page(url)
        # 爬取深度
        depth = 1
        while next_page:
            if not self.bf.add(next_page):
                next_page = self.process_title_page(next_page)
            else:
                next_page = None
            if depth == 10:
                return
            depth += 1

    def main(self, start_url):
        soup = self.open_url(start_url)
        # 获得导航栏链接
        nav = soup.find("div", class_="nav")
        result = nav.find_all("li")
        # 去掉#
        result = result[1:-1]

        for each in result:
            nav_href = each.a.get('href')   # 得到每个nav链接
            # print nav_href
            self.process_nav(nav_href)      # 处理每个nav

my_url = 'http://gzrb.gog.cn/index.shtml'

spider = MySpider()
# spider.clean_bloom_filter()
# spider.process_title_page(my_url)
# spider.process_nav(my_url)
spider.main(my_url)
