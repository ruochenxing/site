#!/usr/bin/env python
# encoding=utf-8

SECRET_KEY = 'it is web site'
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


WEB_ROOT = "www.daiguangwang.top"

USE_QN = True
VIEW_IN_QN = True
