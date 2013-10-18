import sys
import os
import logging

import tornado.locale
import tornado.options
import tornado.ioloop
import tornado.web

from setting import settings, db

from controller import main
from controller import todo
from controller import auth
from controller import user

handlers = [
    (r"/", main.MainHandler),
    (r"/login", main.LoginHandler),
    (r"/logout", main.LogoutHandler),
    (r"/register", main.RegisterHandler),
    (r"/profile", auth.AccountSettingHandler),
    (r"/todo_list", todo.TodoListHandler),
    (r"/todo/([^/]+)", todo.TodoHandler),
    (r"/todo_compose", todo.TodoComposeHandler),
    (r"/todo_find", todo.TodoFindHandler),
    (r"/u/(.*)/home", user.HomeHandler),
    ]

if __name__ == "__main__":
    tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), 'language'))
    tornado.locale.set_default_locale('zh_CN')
    application = tornado.web.Application(handlers, **settings)
    application.db = db
    application.listen(settings['port'])
    tornado.ioloop.IOLoop.instance().start()
