import os
import sys
import logging
import uuid

import json
import string

import tornado.web
import tornado.escape
import urlparse
import urllib

import Levenshtein

from controller.base import *

from module.todo_entity import TodoMatchEntity


class TodoListHandler(BaseHandler):
    def get(self):
        
        entries = self.db.query("SELECT * FROM todo WHERE todo_user_id = %s and todo_status = %s "
                                "ORDER BY todo_created_date ", self.current_user.user_id,0)
        if not entries:
            self.redirect("/todo_compose")
            return
        self.render("todo_list.html", entries=entries,title="My Todo")

class TodoHandler(BaseHandler):
    def get(self, slug):
        entry = self.db.get("SELECT * FROM todo WHERE todo_slug = %s", slug)
        if not entry: raise tornado.web.HTTPError(404)

        count = self.db.get('select count(*) from todo_update where todo_id=%s' % entry.todo_id)
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

        self.render("todo.html", entry=entry, updates=updates, times=times, with_update=True)

class TodoDoneHandler(BaseHandler):
    def get(self, slug):
        entry = self.db.get("SELECT * FROM todo WHERE todo_slug = %s", slug)
        if not entry: raise tornado.web.HTTPError(404)
        self.render("todo_done.html", entry=entry)

class TodoDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        
        if id:
            entry = self.db.execute("DELETE FROM todo WHERE todo_id = %s", int(id))
        self.redirect("/todo_list")

class TodoComposeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        action = self.get_argument("action", None)
        if action:
            print "action: "+action
        entry = None
        if id:
            entry = self.db.get("SELECT * FROM todo WHERE todo_id = %s", int(id))
        self.render("todo_compose.html", entry=entry,action=action)
    
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        action = self.get_argument("action", None)
        category = self.get_argument("category", 0)
        what = self.get_argument("what")
        thumb = self.get_argument("todo_thumb",None)
        logo = self.get_argument("todo_logo",None)
        print logo
        
        when = self.get_argument("when")
        if id:
            entry = self.db.get("SELECT * FROM todo WHERE todo_id = %s", int(id))
            if not entry: raise tornado.web.HTTPError(404)
            if action=="update":
                slug = entry.todo_slug
                self.db.execute(
                    "UPDATE todo SET todo_what = %s, todo_when = %s, todo_category = %s,todo_logo_thumb=%s, todo_logo=%s, todo_updated_date=UTC_TIMESTAMP() "
                    "WHERE todo_id = %s", what, when, category, thumb, logo, int(id))
            elif action=="redo":
                slug = str(uuid.uuid1())
            
                self.db.execute(
                    "INSERT INTO todo (todo_user_id,todo_what,todo_when,todo_category,todo_slug,todo_logo_thumb,todo_logo,todo_created_date,todo_updated_date) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,UTC_TIMESTAMP(),UTC_TIMESTAMP())",
                    self.current_user.user_id, what,when,category,slug,thumb,logo)
        else:
            slug = str(uuid.uuid1())
            
            self.db.execute(
                "INSERT INTO todo (todo_user_id,todo_what,todo_when,todo_category,todo_slug,todo_logo_thumb,todo_logo,todo_created_date,todo_updated_date) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,UTC_TIMESTAMP(),UTC_TIMESTAMP())",
                self.current_user.user_id, what,when,category,slug,thumb,logo)
        self.redirect("/todo/" + slug)


class TodoChangeStatusHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        status = self.get_argument("status", None)
        entry = None
        if id and status:
            self.db.execute("UPDATE todo SET todo_status = %s,todo_closed_date=UTC_TIMESTAMP() WHERE todo_id = %s", status,id)
        self.redirect("todo_list")


class TodoShareHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        type = self.get_argument("type", None)
        print id
        print type
        entry = None
        if id and type:
            self.db.execute("UPDATE todo SET todo_type = %s,todo_updated_date=UTC_TIMESTAMP() WHERE todo_id = %s", type,id)
        self.redirect("/todo_list")


class TodoFindHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        
        when_match = 0.3
        what_match = 0.7

        result = []

        id = self.get_argument("id", None)
        page = int(self.get_argument("page",0))
        pagesize=10

        selfentry = None
        if id:
            selfentry = self.db.get("SELECT * FROM todo WHERE todo_id = %s", int(id))
            selfid = selfentry.todo_slug
            #TODO filter out current user's todo
            entries = self.db.query("SELECT t.*, u.nickname,u.language,u.gender FROM todo t left join auth_user u on todo_user_id = user_id WHERE todo_id != %s", int(id))
            if selfentry and entries:

                for entry in entries:
                    
                    match = 0
                    if entry.todo_when == selfentry.todo_when:
                        match = match + when_match
                    
                    match = match + Levenshtein.ratio(entry.todo_what,selfentry.todo_what) * what_match
                    todo_match = TodoMatchEntity(entry.todo_id)
                    todo_match.load(entry)
                    todo_match.todo_match = match
                    result.append(todo_match)

                start = page*pagesize
                end = (page+1)*pagesize-1
                page_result=result[start:end]

                page_result.sort(key=lambda todo_match: todo_match.todo_match, reverse=True)

        total = len(result)
        self.render("todo_find.html", entries=page_result,page=page,totalnum=total,pagesize=pagesize,selfid=selfid,title="Find Todo")


class TodoAchieveListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        
        entries = self.db.query("SELECT * FROM todo WHERE todo_user_id = %s and todo_status = %s "
                                "ORDER BY todo_created_date ", self.current_user.user_id,1)
        self.render("todo_achieve_list.html", entries=entries,title="My Achievement")


class TodoGiveupListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        
        entries = self.db.query("SELECT * FROM todo WHERE todo_user_id = %s and todo_status = %s "
                                "ORDER BY todo_created_date ", self.current_user.user_id,2)
        self.render("todo_giveup_list.html", entries=entries,title="My Giveup")

class TodoRandomJsonHandler(BaseHandler):
    def get(self):
        total = 100
        result = []
        page = self.get_argument("page", None)
        print page
        #TODO filter out the user self's todo
        entries = self.db.query("SELECT t.*, u.nickname,u.language,u.gender FROM todo t left join auth_user u on todo_user_id = user_id WHERE todo_user_id = %s and todo_status = %s "
                                "ORDER BY todo_created_date LIMIT %s", self.current_user.user_id,0,total)
        for entry in entries:
            todo_match = TodoMatchEntity(entry.todo_id)
            todo_match.load(entry)
            result.append(todo_match)
            entry.todo_created_date = entry.todo_created_date.strftime('%Y-%m-%d')
            entry.todo_updated_date = entry.todo_updated_date.strftime('%Y-%m-%d')
        #print entries
        json_result = json.dumps(result, default=lambda a: a.__dict__)
        print json_result
        self.write(json_result)

class TodoWhatsNewHandler(BaseHandler):
    def get(self):
        self.render("todo_whatsnew.html")


