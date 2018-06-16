#!/usr/bin/env python
#-*- coding:utf-8 -*-
#coded by zsdlove
import threading
import urllib
from bs4 import BeautifulSoup
import sys
import os
import requests
import threading
from multiprocessing import Pool, cpu_count
import multiprocessing
import time
lock=threading.Lock()
class scrapy(object):
    def __init__(self,root,threadNum,plugin):
        self.root = root
        self.threadNum = threadNum
        self.new_urls = set()
        self.old_urls = set()
        self.dir_exploit = []
        self.plugin = os.getcwd()+'/' +plugin
        sys.path.append(plugin)
    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
           self.new_urls.add(url)#set中使用add方法添加url对象
#添加新的url
    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)
#判断新连接列表中是否有链接
    def has_new_url(self):
        return len(self.new_urls) != 0
#获得新的连接地址
    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url	
#请求网页		
    def download(self, url,htmls):
        if url is None:
            return None
        craw_content = {}
        try:
            r = requests.get(url, timeout=3)
            if r.status_code != 200:
                return None
            craw_content["html"] = r.text
        except:
            pass
        htmls.append(craw_content)
#判断连接是否属于当前域名	
    def domain_judge(self, domain, url):
        if (url.find(domain) != -1):
            return True
        else:
            return False
#解析页面
    def craw_parse(self,page_url,content):
        if content is None:
            return
        soup = BeautifulSoup(content,'html.parser')
        newUrls = self._get_new_urls(page_url,soup)
        return newUrls
#获得新的url地址
#重爬取的页面的a标签中获取a标签
    def _get_new_urls(self, page_url,soup):
        new_urls = set()
        links = soup.find_all('a')
        for link in links:
            new_url = link.get('href')
            new_full_url = urllib.parse.urljoin(page_url, new_url)
            if(self.domain_judge(self.root,new_full_url)):
                new_urls.add(new_full_url)
        return new_urls
#获得插件列表
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
#加载插件
    def work(self,url,html):
        for _plugin in self.list_plusg():
            try:
                m = __import__(_plugin.split('.')[0])
                spider = getattr(m, 'spider')
                p = spider()
                s =p.run(url,html)
            except:
                pass
#爬虫入口				
    def craw(self):
        count=1
        self.add_new_url(self.root)
        while self.has_new_url():#判断new_urls里是否有新的url
            content = []
            th = []
            for i in list(range(self.threadNum)):
                if self.has_new_url() is False:
                    break
                new_url = self.get_new_url()#获取新的url
                print("craw:" + new_url)
                count=count+1
                t = threading.Thread(target=self.download,args=(new_url,content))
                t.start()
                th.append(t)
            for t in th:
                t.join()
            for craw_content in content:
                if craw_content is None:
                    continue
                new_urls = self.craw_parse(new_url,craw_content.get('html'))#获得新的url列表
                self.work(craw_content.get('url'),craw_content.get('html'))#加载插件
                self.add_new_urls(new_urls)#添加新的urls	
        saveurl(self.root,self.old_urls)
        print("共爬取"+str(count)+"条连接")
def getTargetDomain():
        f=open("url_list","r")
        url_list=[]
        lines=f.readlines()
        for url in lines:
            url=url.split()  
            url_list.append(url[0])
        return url_list	
def oneproc(url):
    scrapy(url,50,'script').craw()
#保存url,方法有问题，暂时不修改
def saveurl(root,urllist):
    root="result/"+root.split('.')[1]+"."+root.split('.')[2]+".txt"
    file=open(root,"a+")
    for link in urllist:
       file.write(link+"\n")	
if __name__ == "__main__":
    #timestart=time.time()
    urls=getTargetDomain()
    #try:
    for url in urls:
           oneproc(url)
    input('Press Enter to exit...')
    #except:
     #   pass
	   