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

from railnation.screen.railnation_screen import Screen

from railnation.core.railnation_errors import ChangePage

from railnation.pages.page_welcome import Page


class Application(object):
    def __init__(self):
        log.info('Application object created.')

        self.pages = {}
        self._load_all_pages()
        log.info('%s pages loaded.' % len(self.pages))

        print('Authorizing on rail-nation.com...')
        authorize()
        log.info('Authorization complete.')

        print('Loading game parameters...')
        load_game()
        log.info('Game parameters loaded.')

        self.screen = Screen()
        log.info('Screen ready.')

    def start(self):
        log.info('Game is starting!')
        current_page = 'welcome'

        while True:
            try:
                page = self.pages[current_page]()
                self.screen.display(page)
            except ChangePage as key:
                log.debug('Changing page to: %s' % key)
                current_page = key

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
