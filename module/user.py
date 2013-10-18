import os
import sys
import logging

class UserEntity(object):
    def __init__(self, user_id):
        self.user_id = user_id
        #self.prefs = {"locale": "zh_CN"}
        self.prefs = {}

    def load(self, entity):
        self.nickname = entity.nickname
        self.prefs['locale'] = entity.language
        self.email = entity.email

