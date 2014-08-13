# -*- coding:utf-8 -*-
"""docstring"""

import time

from railnation.core.railnation_globals import log

import railnation.core.railnation_client  # create client instance

from railnation.core.railnation_auth import authorize
from railnation.core.railnation_params import load_game

from railnation.core.railnation_screen import Screen


class Application(object):
    def __init__(self):
        log.info('Main object created.')

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
        while True:
            self.screen.update()
            time.sleep(0.1)

    def end(self):
        self.screen.end()
