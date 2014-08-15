# -*- coding:utf-8 -*-
"""Logic"""
import os
import sys

from railnation.core.railnation_globals import (
    log,
    pages_path,
    orig_sys_path,
)
from railnation.screen.railnation_menu import menu
import railnation.core.railnation_client  # creates client instance
from railnation.core.railnation_authentication import authorize
from railnation.core.railnation_params import load_game
from railnation.core.railnation_errors import ChangePage


class Application(object):
    def __init__(self):
        log.info('Application object created.')

        self.pages = {}
        self._load_all_pages()
        log.info('%s pages loaded.' % len(self.pages))

        print('Connecting to www.rail-nation.com...')

        authorize()
        log.info('Authorization complete.')

        load_game()
        log.info('Game parameters loaded.')

        # now it is safe to import screen (it uses client)
        from railnation.screen.railnation_screen import Screen
        self.screen = Screen()
        log.info('Screen ready.')

    def start(self):
        log.info('Game is starting!')
        current_page = self.pages['welcome']()

        while True:
            try:
                self.screen.display(current_page)
            except ChangePage as key:
                log.debug('Changing page to: %s' % key)
                current_page = self.pages[key]()

    def end(self):
        self.screen.end()

    def _load_all_pages(self):
        """import all pages in railnation.pages dir"""
        header = 'page_'
        for item in os.listdir(pages_path):
            if item.startswith(header) and item.endswith(".py"):
                log.debug("Importing file %s" % item)
                page_module = __import__(os.path.basename(item)[:-3])
                self.pages[page_module.Page.name] = page_module.Page
                if page_module.Page.key != '':
                    menu.add_entry(page_module.Page)
        # Restore system path
        sys.path = orig_sys_path
