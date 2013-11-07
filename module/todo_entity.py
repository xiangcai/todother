import os
import sys


class TodoMatchEntity(object):
    def __init__(self, todo_id):
        self.todo_id = todo_id

    def load(self, entity):
        self.todo_slug = entity.todo_slug
        self.user_name = entity.nickname
        self.todo_what = entity.todo_what
        self.todo_when = entity.todo_when
        self.todo_thumb = entity.todo_logo_thumb
        self.todo_logo = entity.todo_logo
        self.user_language = entity.language
        self.user_gender = entity.gender
        self.todo_created_date = entity.todo_created_date.strftime('%Y-%m-%d')
        self.todo_updated_date = entity.todo_updated_date.strftime('%Y-%m-%d')
        self.todo_distance = None
        self.todo_match = 0