import os
import sys
import logging
import uuid

import tornado.web
import tornado.escape

import Levenshtein

from controller.base import *

from module.todo_entity import TodoMatchEntity


class TodoListHandler(BaseHandler):
    def get(self):
        
        entries = self.db.query("SELECT * FROM todo ORDER BY todo_created_date ")
        if not entries:
            self.redirect("/todo_compose")
            return
        self.render("todo_list.html", entries=entries,title="My Todo")

class TodoHandler(BaseHandler):
    def get(self, slug):
        entry = self.db.get("SELECT * FROM todo WHERE todo_slug = %s", slug)
        if not entry: raise tornado.web.HTTPError(404)
        self.render("todo.html", entry=entry)


class TodoComposeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id = self.get_argument("id", None)
        entry = None
        if id:
            entry = self.db.get("SELECT * FROM todo WHERE todo_id = %s", int(id))
        self.render("todo_compose.html", entry=entry)
    
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        
        what = self.get_argument("what")
        
        when = self.get_argument("when")
        if id:
            entry = self.db.get("SELECT * FROM todo WHERE todo_id = %s", int(id))
            if not entry: raise tornado.web.HTTPError(404)
            slug = entry.todo_slug
            self.db.execute(
                "UPDATE todo SET todo_what = %s, todo_when = %s, todo_updated_date=UTC_TIMESTAMP()"
                "WHERE todo_id = %s", what, when, int(id))
        else:
            slug = str(uuid.uuid1())
            
            self.db.execute(
                "INSERT INTO todo (todo_user_id,todo_what,todo_when,todo_slug,todo_created_date,todo_updated_date)"
                "VALUES (%s,%s,%s,%s,UTC_TIMESTAMP(),UTC_TIMESTAMP())",
                self.current_user.user_id, what,when,slug)
        self.redirect("/todo/" + slug)


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
                        match = match + 1 * when_match
                    
                    match = match + Levenshtein.ratio(entry.todo_what,selfentry.todo_what)
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


