from lib import utils

__author__ = 'caninemwenja'

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import tornado.ioloop
import tornado.web
import sockjs.tornado
import logging
import sys
import os
import json

logging.getLogger().setLevel(logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class IndexHandler(tornado.web.RequestHandler):

    def jinja_render(self, template_name, **kwargs):
        template_dirs = [os.path.join(BASE_DIR, "templates"),]

        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)

        content = template.render(kwargs)
        self.write(content)

    def get(self, *args, **kwargs):
        self.jinja_render("index.html")


class MarkerServer(sockjs.tornado.SockJSConnection):

    def on_open(self, request):
        logging.info("Received connection from: "+str(request))

    def on_close(self):
        logging.info("Connection closed")

    def on_message(self, message):
        logging.info("Received message: "+str(message))

        data = json.loads(message)

        teacher = data['teacher']
        student = data['student']

        result = utils.similarity(teacher, student, **data)

        self.send(json.dumps(result, default=lambda x: str(x)))


def main():
    logging.info("Starting Server...")

    router = sockjs.tornado.SockJSRouter(MarkerServer, "/marker")

    settings = {
        'debug': True,
        'static_path': os.path.join(BASE_DIR, 'static'),
    }

    handlers = [
        (r"/", IndexHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler),
    ]

    handlers += router.urls

    app = tornado.web.Application(handlers, **settings)

    port = 8080
    if len(sys.argv) > 1:
        port = sys.argv[1]

    app.listen(port)

    logging.info("Listening...")

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        logging.info("Bye!")


if __name__ == "__main__":
    main()