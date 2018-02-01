#!/usr/bin/env python
#-*- coding:utf-8 -*-
#coded by zsdlove
import threading
from urlparse import urljoin
from bs4 import BeautifulSoup
import sys
import os
import requests
class scrapy(object):
    def __init__(self,root,threadNum,plugin,disallow):
        self.root = root
        self.threadNum = threadNum
        self.new_urls = set()
        self.old_urls = set()
        self.dir_exploit = []
        self.disallow = ['__init__']
        self.disallow.extend('sqlcheck')
        self.plugin = os.getcwd()+'/' +plugin
        sys.path.append(plugin)
		
    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)

    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)

    def has_new_url(self):
        return len(self.new_urls) != 0

    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url	
		
    def download(self, url,htmls):
        if url is None:
            return None
        _str = {}
        _str["url"] = url
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                return None
            _str["html"] = r.text
        except Exception, e:
            print Exception,":",e
        htmls.append(_str)
		
    def _judge(self, domain, url):
        if (url.find(domain) != -1):
            return True
        else:
            return False

    def _parse(self,page_url,content):
        if content is None:
            return
        soup = BeautifulSoup(content, 'html.parser')
        _news = self._get_new_urls(page_url,soup)
        return _news

    def _get_new_urls(self, page_url,soup):
        new_urls = set()
        links = soup.find_all('a')
        for link in links:
            new_url = link.get('href')
            new_full_url = urljoin(page_url, new_url)
            if(self._judge(self.root,new_full_url)):
                new_urls.add(new_full_url)
        return new_urls

    def list_plusg(self):
        def filter_func(file):
            if not file.endswith(".py"):
                return False
            for disfile in self.disallow:
                if disfile in file:
                    return False
            return True
        dir_exploit = filter(filter_func, os.listdir(self.plugin))
        return list(dir_exploit)

    def work(self,url,html):
        for _plugin in self.list_plusg():
            try:
                m = __import__(_plugin.split('.')[0])
                spider = getattr(m, 'spider')
                p = spider()
                s =p.run(url,html)
            except Exception,e:
                print Exception,":",e 
				
    def craw(self):
        self.add_new_url(self.root)
        while self.has_new_url():
            _content = []
            th = []
            for i in list(range(self.threadNum)):
                if self.has_new_url() is False:
                    break
                new_url = self.get_new_url()
                print("craw:" + new_url)
                t = threading.Thread(target=self.download,args=(new_url,_content))
                t.start()
                th.append(t)
            for t in th:
                t.join()
            for _str in _content:
                if _str is None:
                    continue
                new_urls = self._parse(new_url,_str.get('html','default'))
                #disallow = ["sqlcheck"]
                disallow=["sqlcheck","xss_check"]
                self.work(_str.get('url','default'),_str.get('html','default'))
                self.add_new_urls(new_urls)
disallow=["sqlcheck","xss_check"]
s=scrapy('http://www.szxcc.com',10,'script',disallow)
s.craw()