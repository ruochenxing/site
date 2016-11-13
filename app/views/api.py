#!/usr/bin/env python
# encoding=utf-8

import os
from flask import *
from ..config import *
from .. import dao
from ..qiniutool import PREFIX_QN

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/download/<hashid>')
def download(hashid):
	file_path = os.path.join(FILE_PATH, hashid)
	return send_file(file_path)


@api.route('/last/<size>')
def last(size):
	size = int(size)
	questions, count = dao.select(QUESTION_COLL, {}, limit=size, skip=0)
	if count > 0:
		results = []
		for q in questions:
			picUrl = ''
			if len(q['answers']) > 0:
				the_ans = dao.select_one(ANSWER_COLL, {'_id': q['answers'][0]})
				picUrl = the_ans['imgs'][0]
			if VIEW_IN_QN:
				picUrl = (PREFIX_QN + "/" + picUrl)
			else:
				picUrl = (WEB_ROOT+"/api/download/" + picUrl)
			results.append({"description": q['title'], "picUrl": picUrl, "title": q['title'], "url": WEB_ROOT + "/zhihu/detail/" + str(q['_id'])})
		return jsonify({"result": "true", "data": results})
	return jsonify({"result": "false"})
