# coding=utf-8

from bs4 import BeautifulSoup
import threading
import Queue
from util import *
from config import *
from ProxyUtil import ProxyUtil
from pymongo import DESCENDING, ASCENDING

MONGO = MongoClient(MONGO_HOST, MONGO_PORT)
proxyUtil = ProxyUtil()
queue = None


def select(coll, ft, skip=0, sort=('updateTime', DESCENDING)):  # 默认更新时间降序
	data1 = MONGO[DB][coll].find(ft).sort(*sort)
	count = data1.count()
	return [x for x in data1.skip(skip)], count


def insert_or_update(coll, data):
	data['updateTime'] = int(time.time())
	MONGO[DB][coll].find_one_and_update({'_id': data['_id']}, {'$set': data}, upsert=True)  # 存在则更新，不存在则插入


# 更新问题的动态
class UpdateOneQuestion(threading.Thread):
	def __init__(self, useProxy, queue, master=False):
		self.queue = queue
		self.useProxy = useProxy
		self.master = master
		threading.Thread.__init__(self)

	def run(self):
		count = 0
		while not self.queue.empty():
			count += 1
			parameters = self.queue.get()
			link_id = parameters[0]
			count_id = parameters[1]
			self.update(link_id, count_id)
			if not self.useProxy and count % 10 == 0:
				pause(5)

	def update(self, link_id, count_id):
		global proxyUtil
		global queue
		time_now = int(time.time())
		questionurl = 'http://www.zhihu.com/question/' + link_id
		proxy = None
		if self.useProxy:
			proxy = proxyUtil.getproxy()
			if proxy is None:
				print "proxy is none"
				if self.master:
					print "begin creating...."
					proxyUtil = ProxyUtil(create=True)
				return
		content = get_content(questionurl, count_id, proxy)
		if content == "FAIL":
			proxyUtil.delproxy(proxy)
			queue.put([link_id, count_id])
			return
		elif content == "404":
			delete_one(HOT_QUESTION_COLL,ft={"_id": int(link_id)})
		soup = BeautifulSoup(content)

		questions = soup.find('div', attrs={'class': 'zg-gray-normal'})

		# Find out how many people focus this question.
		if questions is None:
			if "访问频次过" in content:
				print "IP 已被屏蔽"
				if self.useProxy:
					proxyUtil.delproxy(proxy)
					print "proxy length=", proxyUtil.size()
				return
			else:
				return
		else:
			focus_amount = questions.get_text().replace('\n', '')
			focus_amount = focus_amount.replace(u'人关注该问题', '')
			focus_amount = focus_amount.replace(u'关注', '')

			if focus_amount == u'问题还没有':
				focus_amount = u'0'

		focus_amount = focus_amount.replace(u'问题', '')

		if focus_amount == u'\\xe8\\xbf\\x98\\xe6\\xb2\\xa1\\xe6\\x9c\\x89':  # This is a special case.
			return

		# Find out how many people answered this question.
		answer_amount = soup.find('h3', attrs={'id': 'zh-question-answer-num'})
		if answer_amount is not None:
			answer_amount = answer_amount.get_text().replace(u' 个回答', '')
		else:
			answer_amount = soup.find('div', attrs={'class': 'zm-item-answer'})
			if answer_amount is not None:
				answer_amount = u'1'
			else:
				answer_amount = u'0'

		# Find out the top answer's vote amount.
		top_answer = soup.findAll('span', attrs={'class': 'count'})
		if not top_answer:
			top_answer_votes = 0
		else:
			top_answer_votes = 0
			for t in top_answer:
				t = t.get_text()
				t = t.replace('K', '000')
				t = int(t)
				if t > top_answer_votes:
					top_answer_votes = t

		# print it to check if everything is good.
		if count_id % 1 == 0:
			print str(
				count_id) + " , " + self.getName() + " Update hot_questions set focus = " + focus_amount + " , answer = " + answer_amount + ", updateTime = " + str(
				time_now) + ", topAnswerNum = " + str(top_answer_votes) + " where _id = " + link_id

		data = {"focus": int(focus_amount), "answer": int(answer_amount), "topAnswerNum": top_answer_votes, "_id": int(link_id)}
		insert_or_update(HOT_QUESTION_COLL, data)

		# Find out the topics related to this question
		topics = soup.findAll('a', attrs={'class': 'zm-item-tag'})
		if questions is not None:
			for topic in topics:
				topicname = topic.get_text().replace('\n', '')
				topicurl = topic.get('href').replace('/topic/', '')
				tmp = select_one(TOPIC_COLL, ft={"_id": int(topicurl)})
				if tmp is not None:
					continue
				data = {'_id': int(topicurl), 'name': topicname, 'addTime': int(time.time()), 'updateTime': 0}
				MONGO[DB][TOPIC_COLL].update_one({'_id': data['_id']}, {'$set': data}, upsert=True)


class UpdateQuestions:
	def __init__(self, useProxy):
		self.useProxy = useProxy
		threadNum = QUESTION_THREAD_NUM
		if self.useProxy:
			threadNum = 6
		self.question_thread_amount = int(threadNum)

	def run(self):
		global queue
		queue = Queue.Queue()
		threads = []

		time_now = int(time.time())
		after_add_time = time_now - 24 * 3600 * 14  # 14天内添加的
		results = select(HOT_QUESTION_COLL, {"addTime": {"$gt": after_add_time}, "answer": {"$lt": 8}, "topAnswerNum": {"$lt": 50}}, sort=('addTime', DESCENDING))
		print "questions size:", results[1]
		i = 0
		for index in range(0, len(results[0])):
			row = results[0][index]
			link_id = str(row['_id'])
			queue.put([link_id, i])
			i += 1
		thread_amount = self.question_thread_amount
		for i in range(thread_amount):
			threads.append(UpdateOneQuestion(self.useProxy, queue, master=(i == 1)))

		for i in range(thread_amount):
			threads[i].start()

		for i in range(thread_amount):
			threads[i].join()
		proxyUtil.saveips()
		print 'All task done'


if __name__ == '__main__':
	question_spider = UpdateQuestions(False)
	question_spider.run()
