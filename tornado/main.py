#!/usr/bin/env python3
__author__ = 'nonameitem'

import tornado.web
import tornado.ioloop
import tornado.httpserver

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('This is tornado <a href="/">check django</a>')

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    server = tornado.httpserver.HTTPServer(application)
    server.bind(8889)
    server.start(0)  # forks one process per cpu
    tornado.ioloop.IOLoop.current().start()
