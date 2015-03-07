# -*- coding:utf-8 -*-
"""docstring"""

import os.path
import importlib
import logging


class CLI(object):

    def __init__(self):
        self.router = {}

        # construct a router based on modules info
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
                self.router[m.Module.name] = m.Module.api

                logging.debug("Got %s routes for context %s" %
                              (len(m.Module.api), m.Module.name))

        self.context = 'root'
        self.prompt = 'RN> '

    def parse(self, command):
        if len(command) == 0:
            return

        elif command[0] == 'show':
            pass

        elif self.context == 'root' and command[0] in self.router.keys():
            self.context = command[0]
            return self.parse(command[1:])

        elif self.context != 'root':
            if command[0] == 'exit':
                self.context = 'root'
                self.prompt = 'RN> '

            elif command[0] in self.router[self.context].keys():
                try:
                    return {
                        'module': self.context,
                        'action': self.router[self.context][command[0]][0],
                        'args': command[1:],
                    }
                except KeyError:
                    return None