#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from urlparse import urljoin
import time
import redis
import hashlib
r1=redis.Redis(host='127.0.0.1',port=6388,db=0)
def downloader(url):    #web downloader
	resp=requests.get(url,timeout=10)
	#print resp.text
	soup=BeautifulSoup(resp.content,'lxml')
	atag=soup.find_all('a')
	url_list=[]
	for aa in atag:
		try:
			url_list.append(aa['href'])
		except:
			continue
	return url_list
def saveurl(url):
	m=hashlib.md5()
	m.update(url)
	c=m.hexdigest()
	r1.set(c,url)
def scrapy(crawurl):#do url crawl
	urllist=downloader(crawurl)
	for url in urllist:
		fullurl=urljoin(originurl,url)
		if fullurl.find(originurl)!=-1:
			print fullurl
			saveurl(fullurl)
			#time.sleep(0.1)
def main(originurl):
	urllist=downloader(originurl)
	for url in urllist:
		fullurl=urljoin(originurl,url)
		if fullurl.find(originurl)!=-1:
			print fullurl
			scrapy(fullurl)
if __name__ == '__main__':
	originurl="http://www.fpi-inc.com"   #oringin url
	main(originurl)

