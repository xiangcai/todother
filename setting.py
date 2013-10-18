import os
import torndb

from module import uimodules

settings = {
    "cookie_secret": "ubgaqTHURoeUOvOqTghncldpdGhNZQycCzjSbE8alu8kMIwf1xo=",
    "static_path": os.path.join(os.path.dirname(__file__), "static/"),
    "template_path": os.path.join(os.path.dirname(__file__), "templates/"),
    "ui_modules": uimodules,
    "login_url": "/login",
    "xsrf_cookies": True,
    "port": 8088,
    "debug": True,
}


db = torndb.Connection(host="localhost", database="withme", user="root", password="root")

