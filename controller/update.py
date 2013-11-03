import os
import sys
import logging
import json
import string

import tornado.template
import tornado.auth
import tornado.escape
import tornado.web
import tornado.gen

from controller.base import *

class UpdateHandler(BaseHandler):
    def get(self, todo_id):
        self.render("update.html", todo_id=todo_id)

    def post(self, todo_id):
        detail = self.get_argument("detail")
        pic1 = self.get_argument("pic1")
        self.db.execute('insert into todo_update (todo_id, user_id, detail_text, update_time, attach_pic_1) values ("%s", "%s", "%s", UTC_TIMESTAMP(), "%s")' % (todo_id, self.current_user.user_id, detail, pic1))
        #redirect('/todo/%s/story' % todo_id)
        self.write(tornado.escape.json_encode({"success": True}))

class StoryHandler(BaseHandler):
    def get(self, todo_id):
        count = self.db.get('select count(*) from todo_update where todo_id=%s' % todo_id)
        if count == 0:
            updates = None
        elif count > 5:
            updates = self.db.query('select * from todo_update where todo_id=%s order by update_time desc limit 5' % todo_id)
        else:
            updates = self.db.query('select * from todo_update where todo_id=%s order by update_time desc' % todo_id)
        times = []
        if updates:
            for update in updates:
                times.append(update.update_time)
        self.render("story.html", updates=updates, times=times)

    def get_json_result(self, todo_id, begin_id=0, count=10):
        updates = self.db.query('select * from todo_update where todo_id=%s order by update_time desc limit %d,%d' % (todo_id, begin_id, count))
        self.write(tornado.escape.json_encode(updates))

