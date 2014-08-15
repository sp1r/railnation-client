# -*- coding:utf-8 -*-
"""Logic"""

from railnation.core.railnation_globals import log

import railnation.core.railnation_client  # creates client instance
from railnation.core.railnation_authentication import authorize
from railnation.core.railnation_params import load_game

from railnation.screen.railnation_screen import Screen

from railnation.pages.page_welcome import Page


class Application(object):
    def __init__(self):
        log.info('Application object created.')

        # load components here (?)

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
        self.screen.display(Page())

        while True:
            self.screen.display(Page())

    def end(self):
        self.screen.end()
