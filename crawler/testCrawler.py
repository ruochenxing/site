#!/usr/bin/env python
# -*- coding:utf-8 -*-

from CollectionCrawler import *
from QuestionImageCrawler import *

from QuestionCrawler import *
from UpdateQuestion import *
from TopicCrawler import *
from qiniutool import *


# 爬取某个收藏夹的所有回答的图片 cookie
def testCollection(linkId, pageStart, pageEnd):
	collection_crawler = CollectionCrawler(linkId, pageStart, pageEnd)
	collection_crawler.start()


# 爬取某个问题的所有图片 cookie
def testQuestion(linkId):
	question_crawler = QuestionCrawler()
	question_crawler.run(linkId)


# 只需执行一次
def initTopic():
	for topic in BASE_TOPICS:
		TopicCrawler(topic).run()
		pause(5)

######################################

# 以下方法无需cookie
# 根据数据库中已有的topic
# 并获取其question
# 执行前确认是否使用代理


def testTopic(useProxy=False):
	updateTopic = UpdateTopics(useProxy)
	updateTopic.run()


# 更新问题的动态
# 执行前确认是否使用代理
def testHotQuestion(useProxy):
	updateQuestions = UpdateQuestions(useProxy)
	updateQuestions.run()


def uploadAllFile():
	for f in os.listdir(FILE_PATH):
		if os.path.isfile(FILE_PATH+"/"+f):
			print f
			QiuNiuTool.uploadfile(f, f)


def deleteAllFile():
	for f in os.listdir(FILE_PATH):
		if os.path.isfile(FILE_PATH+"/"+f):
			QiuNiuTool.deletefile(f)


def begin(argv):
	if len(argv) <= 1:
		print "参数错误,参考如下:"
		print "爬取某个收藏夹的带逛图片：	crawlerCollection 69135664 1 1"
		print "爬取某个问题的带逛图片：		crawlerQuestion linkId"

		print "爬取新的问题：				crawlerNewQuestion 1/0(是否使用代理)"
		print "更新问题的动态：			UpdateHotQuestions 1/0(是否使用代理)"

		print "上传所有文件到七牛:			uploadAllFile"
		print "删除刚才上传的文件:			deleteAllFile"
		return
	method = argv[1]
	if "crawlerCollection" == method:
		if len(argv) != 5:
			print "参数错误"
			print "爬取某个收藏夹的带逛图片：crawlerCollection 69135664 1 1"
			return
		else:
			linkId = str(argv[2])
			pageStart = int(argv[3])
			pageEnd = int(argv[4])
			if pageStart > pageEnd:
				print "分页参数错误"
				return
			else:
				testCollection(linkId, pageStart, pageEnd)
	elif "crawlerNewQuestion" == method:
		if len(argv) == 3:
			if int(argv[2]) == 1:
				testTopic(True)
				return
		testTopic(False)
	elif "initTopic" == method:
		initTopic()
	elif "UpdateHotQuestions" == method:
		if len(argv) == 3:
			if int(argv[2]) == 1:
				testHotQuestion(True)
				return
		testHotQuestion(False)
	elif "crawlerQuestion" == method:
		if len(argv) != 3:
			print "参数错误"
			print "爬取某个问题的带逛图片：	testQuestion linkId"
			return
		else:
			linkId = str(argv[2])
			testQuestion(linkId)
	elif "uploadAllFile" == method:
		uploadAllFile()
	elif "deleteAllFile" == method:
		deleteAllFile()


if __name__ == "__main__":
	begin(sys.argv)
