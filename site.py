#!/usr/bin/env python
# encoding=utf-8

import sys

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
# from werkzeug.contrib.fixers import ProxyFix
from xtls.logger import get_logger

from app import create_app
from app import config

app = create_app()
# app.wsgi_app = ProxyFix(app.wsgi_app)
logger = get_logger(__file__)

if __name__ == '__main__':
	host = config.WEB_ROOT
	port = 8080 if len(sys.argv) < 2 else int(sys.argv[1])
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(port=port, address=host)
	logger.info('lawyer asst server start at {}:{}'.format(host, port))
	IOLoop.instance().start()
