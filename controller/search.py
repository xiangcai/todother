import os
import sys
import logging
import uuid
import re

import json
import string

import tornado.web
import tornado.escape
import urlparse
import urllib

import Levenshtein

from controller.base import *

from module.todo_entity import TodoMatchEntity

_todo_prefix = "t:"
_person_prefix = "p:"
_friend_prefix = "f:"
_pagesize = 30
_page = 0


class SearchHandler(BaseHandler):
    @tornado.web.authenticated



    def post(self):
        
        global _person_prefix
        global _friend_prefix
        global _todo_prefix
        global _page
        global _pagesize

        keyword = self.get_argument("keyword", None)
        _page = int(self.get_argument("page",0))
        _pagesize=30

        print keyword

        if not keyword:
            return

        if keyword.startswith(_person_prefix):
            return self.person_search(keyword)
        elif keyword.startswith(_friend_prefix):
            return self.friend_search(keyword)
        else:
            return self.todo_search(keyword)

    def person_search(self,orakeyword):
        result = []
        keyword = orakeyword[len(_person_prefix):len(orakeyword)]
        entries = self.db.query("SELECT * FROM auth_user WHERE nickname like %s","%%"+keyword+"%%")
        total = len(entries)
        if len(entries)==1:
            user = UserEntity(entries[0].user_id)
            user.load(entries[0])
            result.append(user)
            self.render("search.html", entries=result,page=_page,totalnum=total,pagesize=_pagesize,keyword=orakeyword,title="Search")
        else:
            self.render("search.html", entries=result,page=_page,totalnum=total,pagesize=_pagesize,keyword=orakeyword,title="Search")

    def friend_search(self,orakeyword):
        keyword = orakeyword[len(_friend_prefix):len(orakeyword)]
        self.render("search.html", result=keyword,title="Search Result")

    def todo_search(self,orakeyword):
        if orakeyword.startswith(_todo_prefix):
            keyword = orakeyword[len(_todo_prefix):len(orakeyword)]
        else:
            keyword = orakeyword
        entries = self.db.query("SELECT t.*, u.nickname,u.language,u.gender FROM todo t left join auth_user u on todo_user_id = user_id "
                            "WHERE todo_what like %s","%%"+keyword+"%%")
        
        if len(entries)==1:
            count = self.db.get('select count(*) from todo_update where todo_id=%s' % entries[0].todo_id)
            if count == 0:
                updates = None
            elif count > 5:
                updates = self.db.query('select * from todo_update where todo_id=%s order by update_time desc limit 5' % entry.todo_id)
            else:
                updates = self.db.query('select * from todo_update where todo_id=%s order by update_time desc' % entry.todo_id)
            times = []
            if updates:
                for update in updates:
                    times.append(update.update_time)
            self.render("todo.html", entry=entries[0], updates=updates, times=times, with_update=True)
        else:
            result = []
            for entry in entries:
                todo_match = TodoMatchEntity(entry.todo_id)
                todo_match.load(entry)
                result.append(todo_match)

            start = _page * _pagesize
            end = (_page+1) * _pagesize-1
            page_result=result[start:end]
            total = len(result)
            print type(result[0])
            self.render("search.html", entries=page_result,page=_page,totalnum=total,pagesize=_pagesize,keyword=orakeyword,title="Search")


