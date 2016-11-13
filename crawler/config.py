#!/usr/bin/env python
# encoding=utf-8
# 存放图片地址
FILE_PATH = '/data/images'
# 数据库
MONGO_HOST, MONGO_PORT = '127.0.0.1', 27017
DB = 'dg_site'
# 数据表
ANSWER_COLL = 'answers'
QUESTION_COLL = 'questions'
TOPIC_COLL = 'topics'
HOT_QUESTION_COLL = 'hot_questions'

# 热门问题爬取线程设置
QUESTION_THREAD_NUM = 2
TOPIC_THREAD_NUM = 2
# 热门问题爬取Cookie
COOKIE_1 = {}
# 带逛问题爬取Cookie
COOKIE = {}
