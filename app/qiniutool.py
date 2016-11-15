# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_file
from config import *
import os
import sys
QN_AK = ''
QN_SK = ''
QN_BUCKET_NAME = ''

PREFIX_QN = ''
# 构建鉴权对象
q = Auth(QN_AK, QN_SK)
IMAGE_PATH = FILE_PATH


class QiuNiuTool:
	def __init__(self):
		pass

	@staticmethod
	def uploadfile(localfile, remotefilename, deletelocal=False):
		token = q.upload_token(QN_BUCKET_NAME, remotefilename, 3600)
		localfilepath = QiuNiuTool.getPath(localfile)
		if not os.path.exists(localfilepath):
			print localfilepath, "not exists!"
			return
		ret, info = put_file(token, remotefilename, localfilepath)
		# print info.text_body
		if info.ok():
			if deletelocal:
				os.remove(localfilepath)
			return True
		else:
			print info
			return False

	@staticmethod
	def getPath(filename):
		return os.path.join(IMAGE_PATH, filename)


if __name__ == "__main__":
	argvs = sys.argv
	lfilename = argvs[1]
	b = int(argvs[2])
	QiuNiuTool.uploadfile(lfilename, lfilename, deletelocal=(b == 1))
