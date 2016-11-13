# coding=utf-8
from bs4 import BeautifulSoup
import threading
import Queue
from util import *
from config import *
from pymongo import MongoClient
from pymongo import DESCENDING, ASCENDING
from ProxyUtil import ProxyUtil
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)
proxyUtil = ProxyUtil()


def select(coll, ft, limit=20, skip=0, sort=('updateTime', DESCENDING)):  # 默认更新时间降序
	data1 = MONGO[DB][coll].find(ft).sort(*sort)
	count = data1.count()
	return [x for x in data1.skip(skip).limit(limit)], count


def insert_or_update(coll, data):
	data['updateTime'] = int(time.time())
	MONGO[DB][coll].find_one_and_update({'_id': data['_id']}, {'$set': data}, upsert=True)  # 存在则更新，不存在则插入


# 根据数据库中已有的topic  无需cookie
# 并获取其question
class UpdateOneTopic(threading.Thread):
	def __init__(self, queue, useProxy=False):
		self.queue = queue
		self.useProxy = useProxy
		threading.Thread.__init__(self)

	def run(self):
		while not self.queue.empty():
			t = self.queue.get()
			link_id = t[0]
			count_id = t[1]
			self.find_new_question_by_topic(link_id, count_id)

	def find_question_by_link(self, topic_url, count_id):
		global proxyUtil
		proxy = None
		if self.useProxy:
			proxy = proxyUtil.getproxy()
			if proxy is None:
				print "proxy is none,begin creating....!"
				proxyUtil = ProxyUtil(create=True)
				return
		content = get_content(topic_url, count_id, proxy)
		if content == "FAIL":
			proxyUtil.delproxy(proxy)
			print "proxy size=", proxyUtil.size()
			return 0
		soup = BeautifulSoup(content)
		questions = soup.findAll('a', attrs={'class': 'question_link'})
		time_now = int(time.time())
		count = 0
		for question in questions:
			count += 1
			tem_text = question.get_text()
			tem_id = question.get('href')
			tem_id = tem_id.replace('/question/', '')
			data = {"_id": int(tem_id), "name": tem_text, "focus": 0, "answer": 0, "addTime": time_now, "topAnswerNum": 0}
			insert_or_update(HOT_QUESTION_COLL, data)
		return count

	def find_new_question_by_topic(self, link_id, count_id):
		new_question_amount_total = 0
		i = 0
		for i in range(1, 3):
			if not self.useProxy:
				pause(1)
			topic_url = 'http://www.zhihu.com/topic/' + link_id + '/unanswered?page=' + str(i)
			new_question_amount_one_page = self.find_question_by_link(topic_url, count_id)
			new_question_amount_total = new_question_amount_total + new_question_amount_one_page
			if new_question_amount_one_page <= 2:
				break
		if new_question_amount_total > 0:
			print str(count_id) + " , " + self.getName() + " Finshed TOPIC " + link_id + ", page " + str(
				i) + " ; Add " + str(new_question_amount_total) + " questions."
		insert_or_update(TOPIC_COLL, {'_id': int(link_id)})


class UpdateTopics:
	def __init__(self, useProxy=False):
		self.useProxy = useProxy
		threadNum = TOPIC_THREAD_NUM
		if self.useProxy:
			threadNum = 6
		self.topic_thread_amount = int(threadNum)

	def run(self):
		time_now = int(time.time())
		before_last_vist_time = time_now - 12 * 60 * 60  # 12小时未访问
		queue = Queue.Queue()
		threads = []

		i = 0
		results = select(TOPIC_COLL, {"updateTime": {"$lt": before_last_vist_time}}, sort=('updateTime', ASCENDING))
		print "topic size:", results[1]
		for row in results[0]:
			link_id = str(row['_id'])
			queue.put([link_id, i])
			i += 1

		for i in range(self.topic_thread_amount):
			threads.append(UpdateOneTopic(queue, self.useProxy))

		for i in range(self.topic_thread_amount):
			threads[i].start()

		for i in range(self.topic_thread_amount):
			threads[i].join()
		proxyUtil.display()
		print 'All task done'


if __name__ == '__main__':
	topic_spider = UpdateTopics(False)
	topic_spider.run()
