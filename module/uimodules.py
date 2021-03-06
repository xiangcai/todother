from __future__ import division
import math
import urlparse
import urllib
import tornado.web


class PersonModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/person.html", entry=entry)


class TodoModule(tornado.web.UIModule):
    def render(self, entry, updates=None, times=None, with_update=False):
        if not with_update:
            return self.render_string("modules/todo.html", entry=entry, updates=None, times=None, with_update=False)
        else:
            return self.render_string("modules/todo.html", entry=entry, updates=updates, times=times, with_update=True)

class TodoDoneModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/todo_done.html", entry=entry)

class TodoGiveupModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/todo_giveup.html", entry=entry)
        

class TodoMatchModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/todo_match.html", entry=entry)


def update_querystring(url, **kwargs):
    base_url = urlparse.urlsplit(url)
    query_args = urlparse.parse_qs(base_url.query)
    query_args.update(kwargs)
    for arg_name, arg_value in kwargs.iteritems():
        if arg_value is None:
            if query_args.has_key(arg_name):
                del query_args[arg_name]

    query_string = urllib.urlencode(query_args, True)     
    return urlparse.urlunsplit((base_url.scheme, base_url.netloc,
        base_url.path, query_string, base_url.fragment))

class PageMudule(tornado.web.UIModule):
    """Pagination links display."""

    def render(self, page, page_size, results_count):
        pages = int(math.ceil(results_count / page_size)) if results_count else 0

        def get_page_url(page):
            # don't allow ?page=1
            if page <= 1:
                page = None
            return update_querystring(self.request.uri, page=page)

        next = page + 1 if page < pages else None
        previous = page - 1 if page > 1 else None
       
        return self.render_string('modules/page.html', page=page, pages=pages, next=next,
            previous=previous, get_page_url=get_page_url)

class UpdateEntry(tornado.web.UIModule):
    def render(self, entry, show_comments=False):
        return self.render_string("modules/update_entry.html", entry=entry, show_comments=show_comments)

