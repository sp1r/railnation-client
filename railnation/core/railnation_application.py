# -*- coding:utf-8 -*-
"""Logic"""
import os
import sys

import logging

from railnation.core.railnation_errors import (
    ChangeHandler,
)

from railnation.core.railnation_client import Client

from railnation.core.railnation_globals import (
    handlers_path,
    orig_sys_path,
)


class Application(object):
    def __init__(self, config):
        logging.debug('Creating application with config: %s' % str(config))

        self.context = ''

        self.handlers = {}
        # import all handlers in railnation.handlers directory
        logging.debug('Start loading handlers...')
        header = 'handler_'
        for item in os.listdir(handlers_path):
            logging.debug('Found file: %s' % item)
            if item.startswith(header) and item.endswith(".py"):
                logging.debug("Importing file: %s" % item)
                module = __import__(os.path.basename(item)[:-3])
                logging.debug("Got handler: %s" % module.Handler.name)
                self.handlers[module.Handler.name] = module.Handler
        # Restore system path
        sys.path = orig_sys_path

        logging.info('Loaded handlers: %s' % str(list(self.handlers.keys())))

        logging.debug('Constructing Client object...')
        self.client = Client()

        logging.debug('Authenticating Client object...')
        self.client.authenticate()

        logging.debug('Loading Game parameters...')
        self.client.session.headers.update({'content-type': 'application/json'})
        self.client.load_parameters()

        logging.debug('Application object successfully created.')

    def start(self):
        logging.info('Game is starting!')

        # loop towards eternity
        while True:
            logging.debug('Current context: %s' % self.context)
            logging.debug('Waiting for input...')
            command = input('(%s): ' % self.context).split()
            logging.debug('Got input: %s' % str(command))

            try:
                self.handlers[self.context].execute(command)

            except KeyError:
                self.execute(command)

            except ChangeHandler as key:
                # logging.debug('Changing handler to: %s' % str(key))
                # current_handler = self.handlers[str(key)]()
                pass

    def end(self):
        pass

    def execute(self, command):
        if command[0] == 'show':
            self.show(command[1:])

        elif command[0] == 'help':
            self.help(command[1:])

    def show(self, command):
        pass

    def help(self, command):
        pass