import os
import logging

from setting import db

class TopShare(object):
    def __init__(self):
        self.db = db

def get_top5():
    stories = db.query('select todo_id, todo_slug, todo_what, todo_logo_thumb from todo where todo_logo is not NULL order by todo_like limit 5')
    return stories

