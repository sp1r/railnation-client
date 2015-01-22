#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Initialize software"""

__appname__ = 'railnation-console-client'
__version__ = '0.1.2'
__author__ = 'V.Spiridonov <namelessorama@gmail.com>'
__license__ = ''

# import system libs
import signal
import sys
from optparse import OptionParser
import logging

# import own libs
from rcc.application import Application

from raillib.errors import (
    ConnectionProblem,
    NotAuthenticated,
)


def _signal_handler(signal, frame):
    """Callback for CTRL-C."""
    try:
        app.end()
    except NameError:
        pass
    sys.exit(0)


def load_options(parser):
    pass


def main(argv=None):
    """Main entry point"""
    if argv is None:
        argv = sys.argv

    parser = OptionParser()
    load_options(parser)

    (options, args) = parser.parse_args(argv)

    # configure logging
    logging.basicConfig(filename='/tmp/railnation-debug.log',
                        filemode='w',
                        format='%(levelname)-10s %(asctime)s: %(message)s',
                        datefmt='%d/%m %H:%M:%S',
                        level=logging.DEBUG)

    logging.info('=' * 80)
    logging.info(' ' * 36 + 'New run!' + ' ' * 36)
    logging.info('=' * 80)

    # Share global var
    global app

    # Catch the CTRL-C signal
    signal.signal(signal.SIGINT, _signal_handler)

    try:
        # load application parameters
        logging.debug('Constructing Application object...')
        app = Application(options)

        logging.debug('Starting Application...')
        app.start()

    except ConnectionProblem as err:
        logging.critical('Connection problem.')
        print('Connection problem.')
        logging.critical(err)
        print(err)
        app.end()
        return 3

    except NotAuthenticated as err:
        logging.critical('Authentication problem.')
        print('Authentication problem.')
        logging.critical(err)
        print(err)
        app.end()
        return 2

    except RuntimeError as err:
        logging.critical(err)
        print(err)
        app.end()
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))