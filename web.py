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
from controller import update
from controller import img

handlers = [
    (r"/", main.MainHandler),
    (r"/login", main.LoginHandler),
    (r"/logout", main.LogoutHandler),
    (r"/register", main.RegisterHandler),
    (r"/profile", auth.AccountSettingHandler),
    (r"/todo_list", todo.TodoListHandler),
    (r"/todo/([^/]+)", todo.TodoHandler),
    (r"/todo_done/([^/]+)", todo.TodoDoneHandler),
    (r"/todo_compose", todo.TodoComposeHandler),
    (r"/todo_del", todo.TodoDeleteHandler),
    (r"/todo_giveup_list", todo.TodoGiveupListHandler),
    (r"/todo_find", todo.TodoFindHandler),
    (r"/todo_status", todo.TodoChangeStatusHandler),
    (r"/todo_share", todo.TodoShareHandler),
    (r"/todo_achieve_list", todo.TodoAchieveListHandler),
    (r"/todo_whatsnew", todo.TodoRandomJsonHandler),
    (r"/u/(.*)/home", user.HomeHandler),
    (r"/todo/([^/]+)/update", update.UpdateHandler),
    (r"/todo/([^/]+)/story", update.StoryHandler),
    (r"/img/upload", img.UploadHandler),
    (r"/img/(.*)/delete", img.DeleteHandler),
    (r"/img/(.*)", img.FileHandler),
    ]

if __name__ == "__main__":
    tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), 'language'))
    tornado.locale.set_default_locale('zh_CN')
    application = tornado.web.Application(handlers, **settings)
    application.db = db
    application.listen(settings['port'])
    tornado.ioloop.IOLoop.instance().start()
