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
        self.user_language = entity.language
        self.user_gender = entity.gender
        self.todo_created_date = entity.todo_created_date
        self.todo_updated_date = entity.todo_updated_date
        self.todo_distance = None
        self.todo_match = 0