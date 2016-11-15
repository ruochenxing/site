#!/usr/bin/env python
# -*- coding:utf-8 -*-

from CollectionCrawler import *
from QuestionImageCrawler import *

from QuestionCrawler import *
from UpdateQuestion import *
from TopicCrawler import *
from qiniutool import *


# 爬取某个收藏夹的所有回答的图片 cookie
def collectioncrawler(linkid, pagestart, pageend):
	collection_crawler = CollectionCrawler(linkid, pagestart, pageend)
	collection_crawler.start()


# 爬取某个问题的所有图片 cookie
def questioncrawler(linkid):
	question_crawler = QuestionCrawler()
	question_crawler.run(linkid)


# 只需执行一次
def topiccrawler():
	for topic in BASE_TOPICS:
		TopicCrawler(topic).run()
		pause(5)


######################################

# 以下方法无需cookie
# 根据数据库中已有的topic
# 并获取其question
# 执行前确认是否使用代理


def newquestioncrawler(useproxy=False):
	update_topics = UpdateTopics(useproxy)
	update_topics.run()


# 更新问题的动态
# 执行前确认是否使用代理
def updatequestions(useproxy):
	update_questions = UpdateQuestions(useproxy)
	update_questions.run()


def uploadallfile():
	for f in os.listdir(FILE_PATH):
		if os.path.isfile(FILE_PATH + "/" + f):
			print f
			QiuNiuTool.uploadfile(f, f)


def deleteallfile():
	for f in os.listdir(FILE_PATH):
		if os.path.isfile(FILE_PATH + "/" + f):
			QiuNiuTool.deletefile(f)


def begin(argv):
	if len(argv) <= 1:
		print "参数错误,参考如下:"
		print "爬取某个收藏夹的带逛图片：	collectioncrawler 69135664 1 1"
		print "爬取某个问题的带逛图片：		questioncrawler linkId"

		print "爬取新的问题：				crawlernewquestion 1/0(是否使用代理)"
		print "更新问题的动态：			updatequestions 1/0(是否使用代理)"

		print "上传所有文件到七牛:			uploadallfile"
		print "删除刚才上传的文件:			deleteallfile"
		return
	method = argv[1]
	if "collectioncrawler" == method:
		if len(argv) != 5:
			print "参数错误"
			print "爬取某个收藏夹的带逛图片：crawlerCollection 69135664 1 1"
			return
		else:
			linkid = str(argv[2])
			pagestart = int(argv[3])
			pageend = int(argv[4])
			if pagestart > pageend:
				print "分页参数错误"
				return
			else:
				collectioncrawler(linkid, pagestart, pageend)
	elif "crawlernewquestion" == method:
		if len(argv) == 3:
			if int(argv[2]) == 1:
				newquestioncrawler(True)
				return
		newquestioncrawler(False)
	elif "topiccrawler" == method:
		topiccrawler()
	elif "updatequestions" == method:
		if len(argv) == 3:
			if int(argv[2]) == 1:
				updatequestions(True)
				return
		updatequestions(False)
	elif "questioncrawler" == method:
		if len(argv) != 3:
			print "参数错误"
			print "爬取某个问题的带逛图片：	testQuestion linkId"
			return
		else:
			linkid = str(argv[2])
			questioncrawler(linkid)
	elif "uploadallfile" == method:
		uploadallfile()
	elif "deleteallfile" == method:
		deleteallfile()


if __name__ == "__main__":
	begin(sys.argv)
