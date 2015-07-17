#!/usr/bin/env python3

"""
Very big thanks to this project https://github.com/haridas/RabbitChat. Most of this code I found here and just add
rooms to chat
"""

import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import options, define

import pika
from pika.adapters.tornado_connection import TornadoConnection


# Define available options
define("port", default=8888, type=int, help="run on the given port")
define("cookie_secret", help="random cookie secret")
define("queue_host", default="127.0.0.1", help="Host for amqp daemon")
define("queue_user", default="guest", help="User for amqp daemon")
define("queue_password", default="guest", help="Password for amqp daemon")

PORT = 8889


class PikaClient(object):

    def __init__(self, chat_id):

        # Construct a queue name we'll use for this instance only

        # Giving unique queue for each consumer under a channel.
        self.queue_name = "queue-%s" % (id(self),)
        # Default values
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None
        self.chat_id = chat_id

        # Webscoket object.
        self.websocket = None

    def connect(self):

        if self.connecting:
                print('PikaClient: Already connecting to RabbitMQ')
                return

        print('PikaClient: Connecting to RabbitMQ on localhost:5672, Object: %s' % (self,))

        self.connecting = True

        credentials = pika.PlainCredentials('guest', 'guest')
        param = pika.ConnectionParameters(host='localhost',
                                          port=5672,
                                          virtual_host="/",
                                          credentials=credentials)
        self.connection = TornadoConnection(param,
                                            on_open_callback=self.on_connected)

        # Currently this will close tornado ioloop.
        # self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        print('PikaClient: Connected to RabbitMQ on localhost:5672')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):

        print('PikaClient: Channel Open, Declaring Exchange, Channel ID: %s' %
              (channel,))
        self.channel = channel

        self.channel.exchange_declare(exchange='chat',
                                      type="direct",
                                      callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        print('PikaClient: Exchange Declared, Declaring Queue')
        self.channel.queue_declare(queue=self.queue_name,
                                   exclusive=True,
                                   callback=self.on_queue_declared)

    def on_queue_declared(self, frame):

        print('PikaClient: Queue Declared, Binding Queue')
        self.channel.queue_bind(exchange='chat',
                                queue=self.queue_name,
                                routing_key=self.chat_id,
                                callback=self.on_queue_bound)

    def on_queue_bound(self, frame):
        print('PikaClient: Queue Bound, Issuing Basic Consume')
        self.channel.basic_consume(consumer_callback=self.on_pika_message,
                                   queue=self.queue_name,
                                   no_ack=True)

    def on_pika_message(self, channel, method, header, body):
        print('PikaCient: Message receive, delivery tag #%i' %
              method.delivery_tag)

        # Send the Cosumed message via Websocket to browser.
        self.websocket.write_message(body.decode('utf8'))

    def on_basic_cancel(self, frame):
        print('PikaClient: Basic Cancel Ok')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        tornado.ioloop.IOLoop.instance().stop()

    # def sample_message(self, ws_msg):
    #     # Publish the message from Websocket to RabbitMQ
    #     properties = pika.BasicProperties(
    #         content_type="text/plain", delivery_mode=1)
    #
    #     self.channel.basic_publish(exchange='tornado',
    #                                routing_key='tornado.*',
    #                                body=ws_msg,
    #                                properties=properties)


class Root(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):

        # Send our main document
        self.render("Welcome to tornado, bitches. You shouldn't be here")


class WebSocketServer(tornado.websocket.WebSocketHandler):
    """WebSocket Handler, Which handle new websocket connection."""

    # TODO: dirty hack needs to be fixed
    def check_origin(self, origin):
        return True

    def open(self, chat_id):
        """Websocket Connection opened."""

        # Initialize new pika client object for this websocket.
        self.pika_client = PikaClient(chat_id)

        # Assign websocket object to a Pika client object attribute.
        self.pika_client.websocket = self

        ioloop.add_timeout(1000, self.pika_client.connect)

    def on_message(self, msg):
        pass

    def on_close(self):
        """Closing the websocket.."""
        print("WebSocket Closed")

        # close the RabbitMQ connection...
        self.pika_client.connection.close()


class TornadoWebServer(tornado.web.Application):
    """ Tornado Webserver Application..."""
    def __init__(self):

        # Url to its handler mapping.
        handlers = [(r"/", Root),
                    (r"/chat/(?P<chat_id>\d+)/", WebSocketServer)]

        # Initialize Base class also.
        tornado.web.Application.__init__(self, handlers)


if __name__ == '__main__':

    # Tornado Application
    print("Initializing Tornado Webapplications settings...")
    application = TornadoWebServer()

    # Helper class PikaClient makes coding async Pika apps in tornado easy
    # pc = PikaClient()
    # application.pika = pc  # We want a shortcut for below for easier typing

    # Start the HTTP Server
    print("Starting Tornado HTTPServer on port %i" % PORT)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)

    # Get a handle to the instance of IOLoop
    ioloop = tornado.ioloop.IOLoop.instance()

    # Add our Pika connect to the IOLoop since we loop on ioloop.start
    #ioloop.add_timeout(1000, application.pika.connect)

    # Start the IOLoop
    ioloop.start()
