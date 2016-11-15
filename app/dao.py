#!/usr/bin/env python
# encoding=utf-8

from pymongo import MongoClient
from pymongo import DESCENDING, ASCENDING
from xtls.timeparser import now
from config import *

MONGO = MongoClient(MONGO_HOST, MONGO_PORT)


def select(coll, ft, limit=20, skip=0, sort=('updateTime', DESCENDING)):  # 默认更新时间降序
	data1 = MONGO[DB][coll].find(ft).sort(*sort)
	count = data1.count()
	return [x for x in data1.skip(skip).limit(limit)], count


def select_one(coll, ft):
	return MONGO[DB][coll].find_one(ft)  # ft:{"_id":"28093823"} find_one返回一个dic


def insert(coll, data):
	data['updateTime'] = now()
	MONGO[DB][coll].find_one_and_update({'_id': data['_id']}, {'$set': data}, upsert=True)  # 存在则更新，不存在则插入


def queryhotquestion(time_now, page=1, pagesize=50):
	skip = (page - 1) * pagesize
	limit = pagesize
	after_add_time = time_now - 24 * 3600 * 14  # 14天内添加的
	data1 = MONGO[DB][HOT_QUESTION_COLL].find({"addTime": {"$gt": after_add_time}, "focus": {"$gt": 100}}).sort(
		[("focus", DESCENDING), ("answer", DESCENDING)])
	count = data1.count()
	return [x for x in data1.skip(skip).limit(limit)], count


def querylikequestion(nowtime, page=1, pagesize=50):
<<<<<<< HEAD
	after_add_time = nowtime - 24 * 3600 * 14  # 14天内添加的
	data1 = select(HOT_QUESTION_COLL, ft={"focus": {"$gt": 100}, "addTime": {"$gt": after_add_time}}, limit=pagesize, skip=(page - 1) * pagesize, sort=("answer", ASCENDING))
=======
	before_last_visit_time = nowtime  # - 12 * 3600  # 12小时未访问
	after_add_time = nowtime - 24 * 3600 * 14  # 14天内添加的
	data1 = select(HOT_QUESTION_COLL, ft={"focus": {"$gt": 100}, "updateTime": {"$lt": before_last_visit_time}, "addTime": {"$gt": after_add_time}}, limit=pagesize, skip=(page - 1) * pagesize, sort=("answer", ASCENDING))
>>>>>>> e0b390d2f3982b0777397cb9aa8646138170a8a2
	return data1
