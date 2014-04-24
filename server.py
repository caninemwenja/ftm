__author__ = 'caninemwenja'

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import tornado.ioloop
import tornado.web
import sockjs.tornado
import logging
import sys
import os
import json

import utils

logging.getLogger().setLevel(logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def similarity(sentence1, sentence2, **kwargs):
    print kwargs

    stemmer = kwargs.get('stemmer', 'porter')

    wsd = kwargs.get('wsd', 'adapted')

    sim = kwargs.get('similarity', 'path')

    scoring = kwargs.get('scoring', 'min')

    print stemmer, wsd, sim, scoring

    tokens_1 = utils.tokenize(sentence1, stemmer)
    tokens_2 = utils.tokenize(sentence2, stemmer)

    senses_1 = [utils.wsd(sentence1, token, wsd) for token in tokens_1 if token and len(token) > 0]
    senses_2 = [utils.wsd(sentence2, token, wsd) for token in tokens_2 if token and len(token) > 0]

    rel_mat = utils.relative_matrix(senses_1, tokens_1, senses_2, tokens_2, sim)

    indices = utils.maximum_weight_bipartite(rel_mat)

    candidates = []

    vals = []
    for row, col in indices:
        candidate = {}

        val = rel_mat[row][col]
        vals.append(val)

        candidate['match'] = val
        candidate['word1'] = {
            'token': tokens_1[row],
            'definition': senses_1[row].definition if hasattr(senses_1[row], 'definition') else None,
        }
        candidate['word2'] = {
            'token': tokens_2[col],
            'definition': senses_2[col].definition if hasattr(senses_2[col], 'definition') else None,
        }

        candidates.append(candidate)

    score = min(vals)

    if scoring == 'mean':
        score = 2*sum(vals)/(len(tokens_1)+len(tokens_2))

    result = {
        'score': score,
        'candidates': candidates,
        'tokens_1': tokens_1,
        'tokens_2': tokens_2,
        'senses_1': senses_1,
        'senses_2': senses_2,
        'rel_mat': rel_mat,
    }

    return result


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

        result = similarity(teacher, student, **data)

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