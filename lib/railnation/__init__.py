#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
Console client to http://rail-nation.com browser game.
"""

from __future__ import print_function

__appname__ = 'rail-nation-client'
__version__ = '0.0.0'
__author__ = 'V.Spiridonov <namelessorama@gmail.com>'


import os
import sys
import optparse
import logging
import cherrypy


from railnation.core.server import session
from railnation.core.errors import RailNationClientError
from railnation.core.common import html_dir
from railnation.core.api import RailNationClientAPIv1


def load_options(parser):
    parser.add_option('--version', action='store_true', dest='print_version',
                      default=False,
                      help='print version and exit')

    parser.add_option('-p', '--port', action='store', dest='app_port',
                      default=8080,
                      help='port to start web application on (default = 8080)')

    parser.add_option('-l', '--log-file', action='store', dest='log_file_name',
                      default=None,
                      help='write journal messages to file, default behavior is to write to '
                           'railnation.log in current directory')

    parser.add_option('-d', '--debug', action='store_true', dest='debug_logging',
                      default=False,
                      help='debug logging')


def CORS():
    cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"
    cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE"
    cherrypy.response.headers["Access-Control-Allow-Headers"] = "X-Requested-With,content-type"


class UserInterface():
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/index.html')


def main(argv=None):
    """Main entry point"""
    if argv is None:
        argv = sys.argv

    # Catch the CTRL-C signal
    # signal.signal(signal.SIGINT, _signal_handler)

    parser = optparse.OptionParser()
    load_options(parser)

    (options, args) = parser.parse_args(argv)

    if options.print_version:
        print('Rail-Nation client v.%s' % __version__)
        sys.exit(0)

    # configure logging
    if options.log_file_name is None:
        log_file_name = os.path.join(os.getcwd(), 'railnation.log')
    else:
        log_file_name = options.log_file_name

    if options.debug_logging:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(filename=log_file_name,
                        filemode='a',
                        format='%(asctime)s: %(levelname)8s: %(name)s: %(message)s',
                        datefmt='%Y-%d-%m %H:%M:%S',
                        level=log_level)

    logging.info('Starting Rail-Nation client v.%s' % __version__)

    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = int(options.app_port)
    cherrypy.config.update({'log.screen': False,
                            'log.access_file': '',
                            'log.error_file': '',
                            })
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)

    ui_config = {
        '/index.html': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(html_dir, 'index.html'),
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(html_dir, 'css'),
        },
        '/img': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(html_dir, 'img'),
        },
        '/js': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(html_dir, 'js'),
        },
    }

    api_v1_config = {}

    cherrypy.tree.mount(UserInterface(), '/', ui_config)
    cherrypy.tree.mount(RailNationClientAPIv1(), '/api/v1', api_v1_config)

    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))