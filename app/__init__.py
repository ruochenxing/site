#!/usr/bin/env python
# encoding=utf-8

from flask import Flask

from . import config


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY

    from .views.web import web
    app.register_blueprint(web)

    from .views.api import api
    app.register_blueprint(api)

    
    return app
