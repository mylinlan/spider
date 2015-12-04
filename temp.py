# -*- coding:utf-8 -*-
import requests
import re
import mysql
from bs4 import BeautifulSoup

Msql = mysql.Mysql()


def process_text(my_str):
    my_str = re.sub("http.*?html", "", my_str).encode('utf-8')
    if type(my_str) == 'unicode':
        my_str = my_str.encode('utf-8')
    return my_str.replace(" ", "").replace("　　", "").replace('\n', '')


def open_url(url):
    req = requests.get(url)
    content = req.text
    soup = BeautifulSoup(content)
    return soup


def process_sub_content(result, insert_id):
    for each in result:
        print '\n' + '楼层：'
        # 时间以及作者
        print each.attrs.get('js_restime')
        print each.a.text
        # 内容
        bbs_content = each.select("[class~=bbs-content]")
        text = bbs_content[0].text.strip()
        # 去除链接以及空格
        # text = re.sub("http.*?html", "", text).encode('utf-8')
        # text = text.replace(" ", "").replace("　　", "")
        print process_text(text)
        # print process_text(text)
        replies = each.select('ul li')
        for reply in replies:
            print '回复：'
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
            Msql.insertData('reply', reply_dict)
    # 处理每一层楼


def first_page(url, author, time, insert_id):
    soup = open_url(url)
    # 各层楼的tag
    result = soup.select("[class~=atl-item]")

    # 回复页总页数
    page_id = soup.select("form a")
    if page_id:
        total_page_num = int(page_id[-2].text)
    else:
        total_page_num = 1
    print total_page_num

    # 首层楼的内容
    if result is None:
        return
    main_content = result[0].select("[class~=bbs-content]")
    main_content = main_content[0].text.strip()
    main_text = process_text(main_content)
    reply_dict = {
                "title_id": insert_id,
                "author": author,
                "time": time,
                "text": main_text
                    }
    Msql.insertData('reply', reply_dict)
    result = result[1:]

    process_sub_content(result, '1')

    if total_page_num > 1:
        for num in range(2, total_page_num + 1):
            print '第'+str(num)+'页'
            next_url = url[:-7]+str(num)+url[-6:]
            print next_url
            new_soup = open_url(next_url)
            result = new_soup.select("[class~=atl-item]")
            process_sub_content(result, insert_id)


my_url = 'http://bbs.tianya.cn/post-333-678733-1.shtml'
first_page(my_url, "lin", "2015-12-2 12:23:34", "1")