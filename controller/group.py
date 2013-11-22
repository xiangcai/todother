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



from controller.base import *

class MessageBuffer(object):
    def __init__(self):
        print "init message buffer"
        self.waiters = set()
        self.cache = []
        self.cache_size = 200

    def wait_for_messages(self, callback, cursor=None):
        if cursor:
            new_count = 0
            for msg in reversed(self.cache):
                if msg["id"] == cursor:
                    break
                new_count += 1
            if new_count:
                callback(self.cache[-new_count:])
                return
        print callback
        self.waiters.add(callback)
        print len(self.waiters)

    def cancel_wait(self, callback):
        self.waiters.remove(callback)

    def new_messages(self, messages):
        print "Sending new message to %r listeners", len(self.waiters)
        logging.info("Sending new message to %r listeners", len(self.waiters))
        for callback in self.waiters:
            try:
                print messages
                callback(messages)
            except:
                print "Error in waiter callback"
                logging.error("Error in waiter callback", exc_info=True)
        self.waiters = set()
        self.cache.extend(messages)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]


# Making this a non-singleton is left as an exercise for the reader.
global_message_buffer = MessageBuffer()
global_chat_group = {}

class GroupNewHandler(BaseHandler):
    @tornado.web.authenticated

    def get(self):
        todo_id = self.get_argument("todo_id", None)
        self_id = self.get_argument("self_id", None)
        
        if todo_id and self_id:
            todo = self.db.get("SELECT * FROM todo WHERE todo_id = %s", int(todo_id))
            if not todo: raise tornado.web.HTTPError(404)

            if todo.todo_group_id:
                self.db.execute(
                        "UPDATE todo SET todo_group_id=%s,todo_group_slug=%s WHERE todo_id in (%s)",
                        todo.todo_group_id,todo.todo_group_slug,self_id)

                entries = self.db.query("SELECT m.*, u.nickname FROM group_message m left join auth_user u on gmsg_user_id = user_id WHERE gmsg_group_id = %s " 
                                            "order by gmsg_created_date",todo.todo_group_id)

                    
                message_buffer = MessageBuffer()
                global_chat_group[todo.todo_group_id] = message_buffer
                
                if entries:
                    for entry in entries:
                        message = {
                            "id": entry.gmsg_slug,
                            "from": entry.nickname,
                            "body": entry.gmsg_content,
                        }
                        message_buffer.new_messages([message])
                self.render("group_chat.html", messages=message_buffer.cache,group_id=todo.todo_group_id)
            else:
                gp_slug = str(uuid.uuid1())
                
                gp_id = self.db.execute_lastrowid(
                    "INSERT INTO todo_group (gp_type,gp_name,gp_category,gp_logo,gp_logo_thumb,gp_target_date,gp_status,gp_slug,gp_created_date,gp_updated_date) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,UTC_TIMESTAMP(),UTC_TIMESTAMP())",
                    todo.todo_type,todo.todo_what,todo.todo_category,todo.todo_logo,todo.todo_logo_thumb,todo.todo_when,todo.todo_status,gp_slug)
                
                if gp_id:
                    self.db.execute(
                        "UPDATE todo SET todo_group_id=%s,todo_group_slug=%s WHERE todo_id in (%s,%s)",
                        gp_id,gp_slug,todo_id,self_id)

                   
                    entries = self.db.query("SELECT m.*, u.nickname FROM group_message m left join auth_user u on gmsg_user_id = user_id WHERE gmsg_group_id = %s " 
                                            "order by gmsg_created_date",gp_id)

                    
                    message_buffer = MessageBuffer()
                    global_chat_group[gp_id] = message_buffer
                    
                    if entries:
                        for entry in entries:
                            message = {
                                "id": entry.gmsg_slug,
                                "from": entry.nickname,
                                "body": entry.gmsg_content,
                            }
                            message_buffer.new_messages([message])
                    self.render("group_chat.html", messages=message_buffer.cache,group_id=gp_id)

class GroupChatHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, slug):
        group = self.db.get("SELECT * FROM todo_group WHERE gp_slug = %s", slug)
        if not group: raise tornado.web.HTTPError(404)
        entries = self.db.query("SELECT m.*, u.nickname FROM group_message m left join auth_user u on gmsg_user_id = user_id WHERE gmsg_group_id = %s " 
                                "order by gmsg_created_date",group.gp_id)

        
        message_buffer = MessageBuffer()
        global_chat_group[group.gp_id] = message_buffer
        
        if entries:
            for entry in entries:
                message = {
                    "id": entry.gmsg_slug,
                    "from": entry.nickname,
                    "body": entry.gmsg_content,
                }
                message_buffer.new_messages([message])
        self.render("group_chat.html", messages=message_buffer.cache,group_id=group.gp_id)


class GroupMessageNewHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        group_id = self.get_argument("group_id", None)
        content = self.get_argument("body")
        if group_id:
            
            if global_chat_group.get(group_id):
                message_buffer = global_chat_group[group_id]
            else:
                message_buffer = MessageBuffer()
                global_chat_group[group_id] = message_buffer

            msg_slug = str(uuid.uuid1())
            msg_id = self.db.execute_lastrowid(
                "INSERT INTO group_message (gmsg_slug,gmsg_group_id,gmsg_user_id,gmsg_content,gmsg_created_date) "
                "VALUES (%s,%s,%s,%s,UTC_TIMESTAMP())",
                msg_slug,group_id,self.current_user.user_id,content)

            message = {
                "id": msg_slug,
                "from": self.current_user.nickname,
                "body": content,
            }
            # to_basestring is necessary for Python 3's json encoder,
            # which doesn't accept byte strings.
            message["html"] = tornado.escape.to_basestring(
                self.render_string("group_message.html", message=message))
            
            if self.get_argument("next", None):
                self.redirect(self.get_argument("next"))
            else:
                self.write(message)
            message_buffer.new_messages([message])
            


class GroupMessageUpdatesHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        cursor = self.get_argument("cursor", None)
        group_id = self.get_argument("group_id", None)
        print "group_id:"+group_id
        if group_id:
            
            if global_chat_group.get(group_id):
                self.message_buffer = global_chat_group[group_id]
            else:
                self.message_buffer = MessageBuffer()
                global_chat_group[group_id] = self.message_buffer
        
        self.message_buffer.wait_for_messages(self.on_new_messages,
                                                cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        print "callback"
        if self.request.connection.stream.closed():
            return
        self.finish(dict(messages=messages))

    def on_connection_close(self):
        self.message_buffer.cancel_wait(self.on_new_messages)

            