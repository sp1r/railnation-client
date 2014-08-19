# -*- coding:utf-8 -*-
"""Logic"""
import os
import sys

from railnation.core.railnation_log import log
log.debug('Loading module: Application')

from railnation.core.railnation_errors import ChangeHandler

from railnation.core.railnation_globals import (
    menu,
    pages_path,
    orig_sys_path,
    screen,
)

FIRST_HANDLER = 'welcome'


class Application(object):
    def __init__(self):
        log.info('Application instantiated.')
        self.handlers = {}

    def start(self):
        log.info('Game is starting!')
        current_handler = self.handlers[FIRST_HANDLER]()

        while True:
            try:
                current_handler.loop()
            except ChangeHandler as key:
                log.debug('Changing handler to: %s' % key)
                current_handler = self.handlers[key]()

    def end(self):
        try:
            screen.end()
        except:
            pass

    def _load_all_handlers(self):
        """import all handlers in railnation.handlers directory"""
        header = 'handler_'
        for item in os.listdir(pages_path):
            if item.startswith(header) and item.endswith(".py"):
                log.debug("Importing file %s" % item)
                module = __import__(os.path.basename(item)[:-3])
                self.handlers[module.Handler.name] = module.Handler
                menu.add_entry(module.Handler)
        # Restore system path
        sys.path = orig_sys_path
