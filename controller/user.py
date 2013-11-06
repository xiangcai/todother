import os
import sys
import logging

import tornado.web
import tornado.escape

from controller.base import *

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, username):
        self.render('home.html', username=self.current_user.nickname)

