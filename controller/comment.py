import os
import sys
import datetime

import tornado.template
import tornado.auth
import tornado.escape
from tornado.log import app_log

from controller.base import *

class CommentHandler(BaseHandler):
    def get(self):
        update_id = self.get_argument("update_id")
        self.render("comment.html", update_id=update_id)

    def post(self):
        update_id = self.get_argument("update_id")
        todo_id = self.db.get('select todo_id from todo_update where id=%s', update_id)['todo_id']
        content = self.get_argument("content")
        comment_id = self.db.execute('insert into todo_comment (todo_id, update_id, comment_text, user_id, comment_time)' + 
                ' values(%d, %s, "%s", "%s", UTC_TIMESTAMP())' % (todo_id, update_id, content, self.current_user.user_id))
        ret = '<div><div><span>' + self.current_user.nickname + '</span></div>'
        ret += '<div><p>' + content + '</p></div>'
        ret += '<div><span>' + datetime.datetime.now().isoformat() + '</span></div></div>'
        self.write(tornado.escape.json_encode({'success': True, 'new_comment': ret}))

