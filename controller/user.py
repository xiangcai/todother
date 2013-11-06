import os
import sys
import logging

import tornado.web
import tornado.escape

from controller.base import *

from module.share import get_top5

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, username):
        self.render('home.html', username=self.current_user.nickname, top_stories=get_top5())

