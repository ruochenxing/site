#!/usr/bin/env python
# encoding=utf-8

from flask import *
from flask_paginate import Pagination

from .. import dao
# from crawler.CollectionCrawler import *
import time
from ..qiniutool import *
web = Blueprint('web', __name__)

PAGE_SIZE = 5
HOT_PAGE_SIZE = 20


@web.route('/')
def index():
	data = {
		'active': 'index',
		'title': u'首页'
	}
	return render_template('index.html', **data)


@web.route('/zhihu')
@web.route('/zhihu/<int:page>')
def zhihu(page=1):
	questions, count = dao.select(QUESTION_COLL, {}, limit=PAGE_SIZE, skip=(page - 1) * PAGE_SIZE)
	for q in questions:
		imgs = []
		for answer in q['answers']:
			the_ans = dao.select_one(ANSWER_COLL, {'_id': answer})
			imgs.extend(the_ans['imgs'])
			if len(imgs) >= 5:
				break
		q['imgs'] = imgs[:5]
	data = {
		'active': 'zhihu',
		'title': u'知乎带逛',
		'questions': questions,
		'view_in_qn': VIEW_IN_QN,
		'prefix_url': PREFIX_QN,
		'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=count, css_framework='bootstrap3')
	}
	return render_template('zhihu.html', **data)


@web.route('/zhihu/detail/<qid>')
@web.route('/zhihu/detail/<qid>/<int:page>')
def detail(qid, page=1):
	q = dao.select_one(QUESTION_COLL, {'_id': qid})
	answers = []
	for answer in q['answers'][(page - 1) * PAGE_SIZE:page * PAGE_SIZE]:  # 分页获取answer id
		answers.append(dao.select_one(ANSWER_COLL, {'_id': answer}))
	data = {
		'title': q['title'] + u' - 第 %s 页' % page,
		'answers': answers,
		'question': q,
		'view_in_qn': VIEW_IN_QN,
		'prefix_url': PREFIX_QN,
		'root': WEB_ROOT,
		'pagination': Pagination(page=page, per_page=PAGE_SIZE, total=len(q['answers']), css_framework='bootstrap3')
	}
	return render_template('question.html', **data)


@web.route('/about')
def about():
	data = {
		'active': 'about',
		'root': WEB_ROOT,
		'title': u'关于'
	}
	return render_template('about.html', **data)


@web.route("/like_questions")
@web.route("/like_questions/<int:page>")
def like_questions(page=1):
	if page <= 0:
		page = 1
	questions, count = dao.querylikequestion(int(time.time()), page, pagesize=HOT_PAGE_SIZE)
	data = {
		'active': 'like',
		'title': u'知乎集赞问题',
		'questions': questions,
		'pagination': Pagination(page=page, per_page=HOT_PAGE_SIZE, total=count, css_framework='bootstrap3')
	}
	return render_template('questions.html', **data)


@web.route("/hot_questions")
@web.route("/hot_questions/<int:page>")
def hot_questions(page=1):
	if page <= 0:
		page = 1
	questions, count = dao.queryhotquestion(int(time.time()), page, pagesize=HOT_PAGE_SIZE)
	data = {
		'active': 'hot',
		'title': u'知乎热门问题',
		'questions': questions,
		'pagination': Pagination(page=page, per_page=HOT_PAGE_SIZE, total=count, css_framework='bootstrap3')
	}
	return render_template('questions.html', **data)
