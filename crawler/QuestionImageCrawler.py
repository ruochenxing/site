#!/usr/bin/env python
# encoding=utf-8

import json
from time import sleep

from xtls.util import BeautifulSoup
from util import *
from xtls.logger import get_logger

logger = get_logger(__file__)
QUESTION_XHR_URL = 'https://www.zhihu.com/node/QuestionAnswerListV2'
ZHIHU_URL = 'https://www.zhihu.com'
QUESTION_URL = 'https://www.zhihu.com/question/{id}'
ANS_SIZE = 10


# 用于爬取带逛图片的
class QuestionCrawler(BaseCrawler):
	def __init__(self):
		super(QuestionCrawler, self).__init__()
		self._request = load_session()
		self.xsrf = load_xsrf()
		self._request.headers[
			'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
		logger.info('init question crawler done.')

	def _run(self, question_id, offset):
		data = {
			'method': 'next',
			'params': '{"url_token":%s,"pagesize":%d,"offset":%s}' % (question_id, ANS_SIZE, offset),
			'_xsrf': self.xsrf,
		}
		result = self.post(QUESTION_XHR_URL, data=data, timeout=60)
		if result is None:
			print "QuestionImageCrawler.py 37 error"
			return
		rst_json = json.loads(result)

		rst = []
		for index, item in enumerate(rst_json['msg']):
			sleep(1)
			soup = BeautifulSoup(item)
			answer = AnswerParser(soup).parse_imgs()  # self.build_answer_item(soup)
			if not answer:
				continue
			AnswerParser.save(answer)
			rst.append(answer['_id'])
		return rst, len(rst_json['msg']) == ANS_SIZE

	def run(self, question_id):
		url = QUESTION_URL.format(id=question_id)
		print url
		html = self.get(url)
		soup = BeautifulSoup(html)
		question = QuestionParser(soup).parse()
		if question is None:
			logger.error("爬取失败" + url + str(soup))
			return
		question['_id'] = question_id
		for index in range(0, 7):
			ids, has_more = self._run(question_id, index * ANS_SIZE)
			question['answers'].extend(ids)
			QuestionParser.save(question)
			logger.info('update question %s-%s' % (index, question_id))
			if not has_more:
				break
