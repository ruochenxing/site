#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random
import sys
from datetime import timedelta
from pprint import pprint
from config import *
import requests
from tornado import httpclient, gen, ioloop, queues

reload(sys)
sys.setdefaultencoding("utf-8")

USER_AGENTS = [
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
	'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
	'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
	'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
	'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
	'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
]


def random_user_agent():
	return random.choice(USER_AGENTS)


class BaseCrawler(object):
	def __init__(self, **kwargs):
		logger = kwargs.get('logger')
		if logger:
			self._log = logger.info
			self._exception = logger.exception
			del kwargs['logger']
		else:
			self._exception = self._log = pprint
		self.__dict__ = dict(self.__dict__, **kwargs)
		self._request = requests.Session()
		self._request.headers['User-Agent'] = random_user_agent()

	def get_raw(self, url, timeout=30, times=3):
		if times == 0:
			return None
		try:
			return self._request.get(url, timeout=timeout, cookies=COOKIE)
		except Exception, e:
			self._exception(e)
			return self.get_raw(url, timeout=timeout, times=times - 1)

	def get(self, url, timeout=30, times=3):
		raw = self.get_raw(url, timeout=timeout, times=times)
		if raw:
			return raw.content
		return None

	def post_raw(self, url, data, headers=None, timeout=30, times=3):
		if times == 0:
			return None
		try:
			if headers:
				headers = dict(self._request.headers, **headers)
				return self._request.post(url, data=data, headers=headers, timeout=timeout, cookies=COOKIE)
			return self._request.post(url, data=data, timeout=timeout, cookies=COOKIE)
		except Exception, e:
			self._exception(e)
			return self.post_raw(url, data, headers=headers, timeout=timeout, times=times - 1)

	def post(self, url, data, headers=None, timeout=30, times=3):
		raw = self.post_raw(url, data, headers=headers, timeout=timeout, times=times)
		if raw:
			return raw.content
		return None


class AsyncCrawler(object):
	def __init__(self, urls, concurrency=10, results=None):
		urls.reverse()
		self.urls = urls
		self.concurrency = concurrency
		self._q = queues.Queue()
		self._fetching = set()
		self._fetched = set()
		if results is None:
			self.results = []

	@staticmethod
	def fetch(url, **kwargs):
		fetch = getattr(httpclient.AsyncHTTPClient(), 'fetch')
		return fetch(url, raise_error=False, **kwargs)

	def handle_html(self, url, html):
		pass

	def handle_response(self, url, response):
		if response.code == 200:
			self.handle_html(url, response.body)
		elif response.code == 599:  # retry
			self._fetching.remove(url)
			self._q.put(url)

	@gen.coroutine
	def get_page(self, url):
		try:
			response = yield AsyncCrawler.fetch(url)
		except Exception as e:
			raise gen.Return(e)
		raise gen.Return(response)

	@gen.coroutine
	def _run(self):
		@gen.coroutine
		def fetch_url():
			current_url = yield self._q.get()
			try:
				if current_url in self._fetching:
					return
				# print('fetching****** %s' % current_url)
				self._fetching.add(current_url)

				response = yield self.get_page(current_url)
				self.handle_response(current_url, response)  # handle reponse

				self._fetched.add(current_url)

				for i in range(self.concurrency):
					if self.urls:
						yield self._q.put(self.urls.pop())
			finally:
				self._q.task_done()

		@gen.coroutine
		def worker():
			while True:
				yield fetch_url()

		self._q.put(self.urls.pop())

		for _ in range(self.concurrency):
			worker()

		yield self._q.join(timeout=timedelta(seconds=300000))

		try:
			assert self._fetching == self._fetched
		except AssertionError:
			print(self._fetching - self._fetched)
			print(self._fetched - self._fetching)

	def run(self):
		io_loop = ioloop.IOLoop.current()
		io_loop.run_sync(self._run)
