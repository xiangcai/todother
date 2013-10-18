import tornado.web
import tornado.escape

from auth import *

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_json = self.get_secure_cookie("WithMe_user")
        if not user_json: return None
        user_id = tornado.escape.xhtml_escape(user_json)
        user = UserEntity(user_id)
        user_row = self.db.query('select * from auth_user where user_id="%s"' % user_id)
        user.load(user_row[0])
        return user

    def get_user_locale(self):
        if (not self.current_user) or ("locale" not in self.current_user.prefs):
            return None
        return self.current_user.prefs["locale"]
