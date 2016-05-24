#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'Nisests'

import requests
import re
import json
import os
from bs4 import BeautifulSoup

search_url = 'http://search.jd.com/Search?keyword='

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'search.jd.com',
    'Referer': 'http://www.jd.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
}


class JDCrawer(object):
    def __init__(self, start_url, key):
        self._start_url = start_url
        self._key = key

    def craw(self):
        s = requests.session()
        req = s.get(self._start_url, headers=headers)
        page_num = self.get_page_num(str(req.content))
        urls = []
        for i in range(int(page_num)):
            urls.append(self._start_url + '&page=' + str((i + 1) * 2))

        # start
        result_list = []
        for url in urls:
            req = s.get(url, headers=headers)
            soup = BeautifulSoup(req.content.decode('utf-8'), 'lxml')
            page_href = soup.select('#J_goodsList > ul > li > div > div.p-img > a')
            page_title = soup.select('#J_goodsList > ul > li > div > div.p-name.p-name-type-2 > a')
            page_price = soup.select('#J_goodsList > ul > li > div > div.p-price > strong')
            for href,title, price in zip(page_href, page_title,page_price):
                # print(title.get('title',-1), 'http:' + href.get('href',-1), price.get('data-price',-1))
                d = {}
                d['title'] = title.get('title',-1)
                d['link'] = 'http:' + href.get('href',-1)
                d['price'] = price.get('data-price',-1)
                result_list.append(d)

        if os.path.isfile('data.json'):
            with open('data.json', 'r') as f:
                data_json = json.load(f)
        else:
            data_json = {}
        data_json[self._key] = result_list
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data_json, f, ensure_ascii=False)

    # 获取搜索结果页数
    def get_page_num(self, data):
        re_page_count = re.compile(r'.*page_count:"(\d+?)"')
        page_num = re_page_count.match(str(data)).group(1)
        return page_num


if __name__ == '__main__':
    # 存储起始链接和关键字
    start_urls = []
    keys = []
    with open('key', 'r') as f:
        for line in f.readlines():
            start_urls.append(search_url + line.strip() + '&enc=utf-8')
            keys.append(line.strip())

    for start_url, key in zip(start_urls, keys):
        print('开始爬取:' + start_url)
        crawl = JDCrawer(start_url, key)
        crawl.craw()