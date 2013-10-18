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
from controller.auth import *
from module.services import randId

class RegisterHandler(BaseHandler):
    def get(self):
        self.render("register.html", title="Register WithME")

    def post(self):
        email = self.get_argument("email")
        nickname = self.get_argument("nickname")
        password = self.get_argument("password")

        urow = self.db.get('select user_id from auth_user where email="%s"' % email)
        result = {'success': True}
        if urow:
            result = {'success': False, 'err_info': 'Email exists'}
        else:
            idrow = self.db.get('show table status like "auth_user"')
            newid = idrow.Auto_increment
            user_id = '10001100%.4d' % randId.new_id()
            self.db.execute('insert into auth_user (user_id, email, nickname, password) values ("%s", "%s", "%s", AES_ENCRYPT("%s", "%d"))' % (user_id, email, nickname, password, newid))
            self.set_secure_cookie("WithMe_user", user_id)
            result['user_id'] = user_id
        self.write(tornado.escape.json_encode(result))

class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">' +
                   self.xsrf_form_html() +
                   'Email: <input type="text" name="email">'
                   'Password: <input type="password" name="password">'
                   '<input type="submit" value="Login">'
                   '</form><a href="/register">Register</a></body></html>')

    def post(self):
        email = self.get_argument("email")
        password = self.get_argument("password")
        if email and password:
            urow = self.db.get('select user_id, AES_DECRYPT(password, id) as password from auth_user where email="%s"' % email)
            if not urow:
                self.redirect('/login?status=invalid_user')
            elif password != urow.password:
                self.redirect('/login?status=wrong_password')
            self.set_secure_cookie("WithMe_user", tornado.escape.xhtml_unescape(urow.user_id))
            self.redirect("/u/%s/home" % urow.user_id)
        else:
            self.redirect("/login?status=error")

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("WithMe_user")
        self.redirect("/")

class MainHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   + self.xsrf_form_html() +
                   'Email: <input type="text" name="email">'
                   'Password: <input type="password" name="password">'
                   '<input type="submit" value="Login">'
                   '</form><a href="/register">Register</a></body></html>')

