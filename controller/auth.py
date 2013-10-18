import os
import sys
import logging

import torndb

from controller.base import *

class AccountSettingHandler(BaseHandler):
    def get(self):
        self.render("profile.html")
