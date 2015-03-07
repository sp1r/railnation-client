# -*- coding:utf-8 -*-
"""docstring"""

import os
import json
import socketserver
import logging
import threading

import daemon.shared


SERVER_SOCK_FILE = os.path.join(daemon.shared.BASE_DIR, 'server.sock')


class DaemonRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # anonymous wont do
        if self.client_address is None:
            logging.info('Anonymous request dropped.')
            return

        logging.debug('Client: %s Sends request: %s' % (self.client_address,
                                                        self.request[0]))

        try:
            d = json.loads(str(self.request[0])[2:-1])
        except ValueError:
            logging.error('Got malformed json object: %s' %
                          str(self.request[0])[2:-1])
            return

        try:
            method = getattr(daemon.shared.THREADS[d['module']], d['action'])
        except KeyError:
            logging.error('Got malformed request: %s' % d)

        except AttributeError:
            logging.error('Got malformed request: %s' % d)

        else:
            result = {'result': method(*d['args'])}

            logging.debug('Sending result: %s' % str(result))
            self.request[1].sendto(bytes(json.dumps(result), 'utf-8'), self.client_address)


class DaemonServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = None
        self.name = 'socket_server'

    def run(self):
        logging.info('Starting server on %s' % SERVER_SOCK_FILE)
        if os.path.exists(SERVER_SOCK_FILE):
            logging.debug('Removing old socket file...')
            os.remove(SERVER_SOCK_FILE)

        self.server = socketserver.UnixDatagramServer(SERVER_SOCK_FILE,
                                                      DaemonRequestHandler)

        self.server.serve_forever()

    def stop(self):
        logging.info('Server is shutting down')
        self.server.shutdown()


if __name__ == '__main__':
    DaemonServer().run()