#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Daemon process doing all the stuff"""

__appname__ = 'railnation-daemon'
__version__ = '0.1.0'
__author__ = 'V.Spiridonov <namelessorama@gmail.com>'


import sys
import os
import signal
import logging
import importlib
import time
import optparse

from railnationlib.game import Game
import daemon.server
import daemon.shared as game


def _signal_handler(signal, frame):
    """Callback for CTRL-C."""
    stop_threads()
    sys.exit(0)


def stop_threads():
    try:
        for t in game.THREADS.values():
            logging.debug('Stopping thread: %s' % t.name)
            t.stop()
            t.join()
    except NameError:
        pass


def load_options(parser):
    parser.add_option('-a', '--auth-file', action='store', dest='auth_filename',
                      default=None,
                      help='read authentication data from file')

    parser.add_option('-l', '--log-file', action='store', dest='log_filename',
                      default=None,
                      help='main log file to write messages to')


def main(argv=None):
    """Main entry point"""
    if argv is None:
        argv = sys.argv

    # Catch the CTRL-C signal
    signal.signal(signal.SIGINT, _signal_handler)

    parser = optparse.OptionParser()
    load_options(parser)

    (options, args) = parser.parse_args(argv)

    if options.log_filename is not None:
        # configure logging
        logging.basicConfig(filename=options.log_filename,
                            filemode='w',
                            format='%(asctime)s: %(levelname)s: %(message)s',
                            datefmt='%d/%m %H:%M:%S',
                            level=logging.DEBUG)

    logging.info('=' * 80)
    logging.info('I`m alive!')

    # import all modules in directory
    base_dir = os.path.realpath(os.path.dirname(__file__))
    modules_dir = os.path.join(base_dir, '..', 'modules')

    logging.debug('Start loading modules...')
    header = 'module_'
    for item in os.listdir(modules_dir):
        logging.debug('Found file: %s' % item)
        if item.startswith(header) and item.endswith(".py"):
            module_path = 'modules.' + os.path.basename(item)[:-3]

            logging.debug("Importing module: %s" % module_path)
            m = importlib.import_module(module_path)
            thread = m.Module(game)

            logging.debug("Got Module: %s" % thread.name)
            game.THREADS[thread.name] = thread
            thread.start()

    if options.auth_filename is not None:
        logging.info('Reading auth data from %s' % options.auth_filename)
        with open(options.auth_filename) as f:
            login = f.readline().rstrip()
            logging.debug('Login: %s' % login)
            password = f.readline().rstrip()
            logging.debug('Got Password')
            world = f.readline().rstrip()
            logging.debug('World ID: %s' % world)

        avatar = Game().get_avatar(login, password, world)

    # start server for clients
    server_thread = daemon.server.DaemonServer()
    game.THREADS['server'] = server_thread
    server_thread.start()

    server_thread.join()
    stop_threads()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))