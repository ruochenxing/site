# -*- coding: utf-8 -*-
import urllib2
from threading import Lock

import BeautifulSoup
import socket
import os
import random

socket.setdefaulttimeout(3)
User_Agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
header = {'User-Agent': User_Agent}
PROXY_URL1 = 'http://www.xicidaili.com/wn/'
PROXY_URL2 = 'http://www.kuaidaili.com/proxylist/'
CHECK_PROXY_URL = "http://ip.chinaz.com/getip.aspx"
DEFAULT_TIMEOUT = 30
lock = Lock()


class ProxyUtil:
	def __init__(self, ippath="ip.txt", create=False):
		self.ippath = ippath
		self.proxies = []
		self.flag = 0
		self.ipmanager = {}
		if create:
			self.saveandvalidproxy()
		self.getproxies()

	def delproxy(self, key):
		if self.ipmanager.get(key["http"]) is None:
			self.ipmanager[key["http"]] = -3
		else:
			self.ipmanager[key["http"]] -= 3
		if self.ipmanager[key["http"]] <= -9:
			if len(self.proxies) > 0 and key in self.proxies:
				self.proxies.remove(key)
				print "proxy size=", self.size()

	def incrementhit(self, key):
		if self.ipmanager.get(key["http"]) is None:
			self.ipmanager[key["http"]] = 1
		else:
			self.ipmanager[key["http"]] += 1

	def size(self):
		return len(self.proxies)

	def saveips(self):
		if len(self.proxies) > 0:
			os.remove(self.ippath)
			f = open(self.ippath, 'a')
			for p in self.proxies:
				f.write(p["http"] + "\n")
			f.flush()
			f.close()

	@staticmethod
	def getcontent(url):
		try:
			req = urllib2.Request(url, headers=header)
			res = urllib2.urlopen(req, timeout=DEFAULT_TIMEOUT).read()
			return res
		except Exception, e:
			print e
			return ""

	def getproxy(self):
		if len(self.proxies) <= 0:
			return None
		else:
			return self.proxies[random.randint(0, len(self.proxies) - 1)]

	def getproxies(self):
		lock.acquire()
		if len(self.proxies) <= 0:
			if os.path.exists(self.ippath):
				f = open(self.ippath)
				lines = f.readlines()
				if len(lines) > 0:
					for i in range(0, len(lines)):
						self.proxies.append({'http': lines[i]})
		lock.release()
		return self.proxies

	def saveandvalidproxy(self):
		lock.acquire()
		try:
			if self.flag == 0:
				self.flag = 1
				proxylist = self.saveproxy()
				valid_proxy = []
				f = open(self.ippath, 'a')
				for p in proxylist:
					res = self.getcontent(CHECK_PROXY_URL)
					if "address" in res:
						print '======' + str(p)
						valid_proxy.append(p)
						f.write(p["http"] + "\n")
				f.flush()
				f.close()
				return valid_proxy
		finally:
			lock.release()

	def saveproxy(self):
		if os.path.exists(self.ippath):
			os.remove(self.ippath)
		res = self.getcontent(PROXY_URL1)
		soup = BeautifulSoup.BeautifulSoup(res)
		ips = soup.findAll('tr')
		proxylist = []
		for x in range(1, len(ips)):
			ip = ips[x]
			tds = ip.findAll("td")
			proxy_host = "http://" + tds[1].contents[0] + ":" + tds[2].contents[0]
			proxy_temp = {"http": proxy_host}
			proxylist.append(proxy_temp)
		for page in range(1, 4):
			res = self.getcontent(PROXY_URL2 + str(page))
			soup = BeautifulSoup.BeautifulSoup(res)
			ips = soup.findAll('tr')
			for x in range(1, len(ips)):
				ip = ips[x]
				tds = ip.findAll("td")
				proxy_host = "http://" + tds[0].contents[0] + ":" + tds[1].contents[0]
				proxy_temp = {"http": proxy_host}
				proxylist.append(proxy_temp)
		return proxylist


if __name__ == "__main__":
	proxyUtil = ProxyUtil(create=True)
	proxy = proxyUtil.getproxy()
	print len(proxyUtil.getproxies())
	# print proxy
	# print str(proxyUtil.getproxies()), len(proxyUtil.getproxies())
