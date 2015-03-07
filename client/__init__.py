#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Console client to railnation-daemon"""

__appname__ = 'railnation-console-client'
__version__ = '0.1.3'
__author__ = 'V.Spiridonov <namelessorama@gmail.com>'


import sys
import os
import signal
import optparse
import logging
import socket
import json

import client.cli


def _signal_handler(signal, frame):
    """Callback for CTRL-C."""
    try:
        pass
    except NameError:
        pass
    sys.exit(0)


def load_options(parser):
    parser.add_option('-c', '--connect', action='store', dest='connect_to',
                      default=None,
                      help='connect to this unix socket')

    parser.add_option('-s', '--socket', action='store', dest='self_socket',
                      default=None,
                      help='listen to this unix socket')

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
    logging.info('Client is here!')

    my_socket = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
    if options.self_socket is not None:
        my_socket_addr = options.self_socket

    else:
         my_socket_addr = '/opt/rail-client/client.sock'

    if os.path.exists(my_socket_addr):
        os.remove(my_socket_addr)

    my_socket.bind(my_socket_addr)

    if options.connect_to is not None:
        server_addr = options.connect_to

    else:
        server_addr = '/opt/rail-daemon/server.sock'

    cli = client.cli.CLI()
    # loop towards eternity
    while True:
        logging.debug('Current context: %s' %
                      cli.context)

        try:
            logging.debug('Waiting for input...')
            command = input(cli.prompt).split()
            logging.debug('Got input: %s' % str(command))

        except EOFError:
            return 0

        else:
            query = cli.parse(command)
            logging.debug('Got query: %s' % query)

            if query is not None:
                my_socket.sendto(bytes(json.dumps(query), 'utf-8'), server_addr)

                result = json.loads(str(my_socket.recv(1024))[2:-1])
                logging.debug('Got result: %s' % result)
                print(result['result'])


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))