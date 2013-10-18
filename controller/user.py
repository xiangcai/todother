import os
import sys
import logging

import tornado.web
import tornado.escape

from controller.base import *

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, username):
        self.write('<html><body>Welcome back ' + self.current_user.nickname +
                   '<a href="/todo_list">My Todo</a> '
                   '<a href="/logout">Logout</a></body></html>')

