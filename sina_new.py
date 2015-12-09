#!/usr/bin/env python
#  encoding: utf-8

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def process_page(html):
    soup = BeautifulSoup(html)
    results = soup.find_all("ul", class_=["list-article", "list-article-more"])
    for result in results:
        titles = result.find_all('li')
        for each in titles:
            print each.h3.a.get('href')
            print each.h3.a.text
            print each.div.find('b').text
            span = each.find('span', class_="time")
            print '2015-'+span.text

driver = webdriver.Firefox()
driver.get("http://gz.sina.com.cn/news/msrd/list.shtml")

for x in range(1, 11):
    time.sleep(2)
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "more-btn"))
        )
    finally:
        print 'start' + '  ' + str(x)

    elem = driver.find_element_by_class_name("more-btn")
    # print elem.get_attribute("class")
    elem.click()
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "more-btn"))
        )
    finally:
        print 'second click'
    elem = driver.find_element_by_class_name("more-btn")
    # print elem.get_attribute("class")
    elem.click()
    if x == 10:
        m_html = driver.page_source
        process_page(m_html)
    next_elem = driver.find_element_by_class_name("next")
    # print elem.get_attribute("class")
    next_elem.click()
    print 'ok end' + '  ' + str(x)

driver.close()