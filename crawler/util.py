#!/usr/bin/env python
# encoding=utf-8
import datetime
import os
import re

import requests
from pymongo import MongoClient
from xtls.codehelper import trytry
from xtls.logger import get_logger
from xtls.timeparser import now
from xtls.util import sha1
from BaseCrawler import BaseCrawler

from config import *

import urllib2
import gzip
import StringIO
import time
from qiniutool import *

logger = get_logger(__file__)
ZHIHU_URL = 'https://www.zhihu.com'
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)
PATTERN_NUM = re.compile(ur'\d+')
PATTERN_IMG = re.compile(ur'"(https://pic[\d].zhimg.com/(v2-)?\w+?_b.\w+)"')


def select_one(coll, ft):
	return MONGO[DB][coll].find_one(ft)


def load_session():
	session = requests.Session()
	return session


def load_xsrf():
	if len(COOKIE) == 0:
		return ""
	else:
		return COOKIE["_xsrf"]


def save(content, filename):
	save_path = FILE_PATH
	if not os.path.exists(save_path):
		os.mkdir(save_path)
	file_path = os.path.join(save_path, filename)
	with open(file_path, 'wb') as fp:
		fp.write(content)
	if USE_QN:
		QiuNiuTool.uploadfile(filename, filename)


class _Parser(BaseCrawler):
	COLL = ''

	def __init__(self, soup):
		super(_Parser, self).__init__()
		self.soup = soup

	@classmethod
	def save(cls, data):
		data['updateTime'] = now()
		return MONGO[DB][cls.COLL].find_one_and_update(
			{'_id': data['_id']},
			{'$set': data},
			upsert=True
		)


class AnswerParser(_Parser):
	COLL = ANSWER_COLL

	def __init__(self, soup):
		super(AnswerParser, self).__init__(soup)

	@classmethod
	def parse_edit_time(cls, soup):
		def parse_time(s):
			s = s.split(u'于')[-1]
			if ':' in s:
				return datetime.datetime.now().strftime('%Y-%m-%d ') + s.strip()
			return s.strip()

		tip = soup.get('data-tip', '')
		if tip:
			return parse_time(tip), parse_time(soup.getText().strip())
		return parse_time(soup.getText().strip()), ''

	def parse_imgs(self):
		answer_soup = self.soup.find('div', class_='zm-editable-content clearfix')
		if not answer_soup:
			if u'回答建议修改：涉及淫秽色情低俗信息' in unicode(self.soup):
				return None
		all_imgs = list(set(PATTERN_IMG.findall(unicode(answer_soup))))
		imgs = []
		for img in all_imgs:
			if isinstance(img, tuple):
				imgs.append(img[0])
			else:
				imgs.append(img)
		# print answer_soup
		# imgs = answer_soup.find('img',class_='origin_image zh-lightbox-thumb lazy')
		if not imgs:
			return None
		answer = {
			'url': ZHIHU_URL + self.soup.find('div', class_='zm-item-rich-text expandable js-collapse-body')[
				'data-entry-url'],
			'agree_cnt': 0, 'a_link': '', 'a_name': u'匿名用户',
			'r_time': '', 'e_time': '', 'comment_cnt': '', 'imgs': [], '_id': '',
		}
		with trytry():
			count = self.soup.find('span', class_='count').getText().strip().lower()
			if 'k' in count:
				count = count[:-1] + '000'
			answer['agree_cnt'] = int(count)

		for img in imgs:
			# img_url=img['src']
			# print img_url
			content = self.get(img, timeout=120)
			if content is None:
				continue
			else:
				filename = sha1(content) + img[img.rfind('.'):]
				save(content, filename)
				# answer['imgs'].append({'local': filename, 'raw': img})
				answer['imgs'].append(filename)

		author = self.soup.find('div', class_='zm-item-answer-author-info')
		author_link = author.find('a', class_='author-link')
		if author_link:
			answer['a_link'] = ZHIHU_URL + author_link['href']
			answer['a_name'] = author_link.getText().strip()

		with trytry():
			answer['r_time'], answer['e_time'] = self.parse_edit_time(self.soup.find('a', class_='answer-date-link'))

		with trytry():
			comment = self.soup.find('a', class_='meta-item toggle-comment js-toggleCommentBox').getText().strip()
			if comment != u'添加评论':
				answer['comment_cnt'] = comment[:-3].strip()
		answer['_id'] = answer['url'].replace('https://www.zhihu.com/question/', '').replace('/answer/', '-')
		return answer


class QuestionParser(_Parser):
	COLL = QUESTION_COLL

	def __init__(self, soup):
		super(QuestionParser, self).__init__(soup)

	def parse(self):
		title = self.soup.find('span', class_='zm-editable-content')
		if title is None:
			logger.error(str(self.soup))
			return None
		question = {
			'title': self.soup.find('span', class_='zm-editable-content').getText().strip(),
			'topics': [],
			'follow_cnt': 0,
			'similarQues': [],
			'_id': '',
			'answers': []
		}
		for topic in self.soup.find_all('a', class_='zm-item-tag'):
			question['topics'].append({
				'topic': topic.getText().strip(),
				'link': ZHIHU_URL + topic['href']
			})
		with trytry():
			question['follow_cnt'] = int(
				PATTERN_NUM.findall(self.soup.find('div', id='zh-question-side-header-wrap').getText())[0])

		with trytry():
			relatedQuestion_ul = self.soup.find('ul', itemprop='relatedQuestion')
			if relatedQuestion_ul:
				for li in self.soup.find('ul', itemprop='relatedQuestion').find_all('li'):
					a = li.find('a')
					question['similarQues'].append({
						'id': a['href'][1 + a['href'].rfind('/'):],
						'title': a.getText().strip()
					})

		return question


def pause(sec):
	print "休眠中.......", str(sec), "s"
	time.sleep(sec)


def get_content(toUrl, count, proxy):
	cookie = COOKIE_1

	headers = {
		'Cookie': cookie,
		'Host': 'www.zhihu.com',
		'Referer': 'http://www.zhihu.com/',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
		'Accept-Encoding': 'gzip'
	}

	req = urllib2.Request(
		url=toUrl,
		headers=headers
	)

	try:
		opener = urllib2.build_opener(urllib2.ProxyHandler())
		if proxy is not None:
			opener = urllib2.build_opener(urllib2.ProxyHandler(proxy))
		urllib2.install_opener(opener)
		page = urllib2.urlopen(req, timeout=20)
		content = page.read()
	except Exception, e:
		if count % 1 == 0:
			print str(count) + ", Error: " + str(e) + " URL: " + toUrl
		return "FAIL"

	if page.info().get('Content-Encoding') == 'gzip':
		data = StringIO.StringIO(content)
		gz = gzip.GzipFile(fileobj=data)
		content = gz.read()
		gz.close()

	return content
