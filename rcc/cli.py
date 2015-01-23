# -*- coding:utf-8 -*-
"""docstring"""

import logging

from rcc.module import ModuleBase


class CLI(object):

    def __init__(self, modules):
        self.context = 'show'
        self.prompt = 'RN> '
        self.router = {
            'show': {}
        }

        self.modules = modules

        for module in self.modules.values():
            assert isinstance(module, ModuleBase)
            for source, keyword in module.routes_in:
                try:
                    self.router[source][keyword] = module
                except KeyError:
                    self.router[source] = {
                        keyword: module
                    }

    def process(self, command):
        if len(command) == 0:
            return

        try:
            self.context, self.prompt = \
                self.router[self.context][command[0]].enter(command)

        except KeyError:
            logging.debug('CLI: router dict key miss.')
            try:
                self.context, self.prompt = \
                    self.modules[self.context].execute(command)
            except KeyError:
                logging.debug('CLI: modules dict key miss.')
                return

        if not self.context in self.modules.keys():
            self.context = 'show'
            self.prompt = 'RN> '