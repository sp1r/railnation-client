# -*- coding:utf-8 -*-
"""docstring"""

import time

from railnation.core.railnation_globals import log
from railnation.core.railnation_screen import Screen
from railnation.core.railnation_client import Client
from railnation.core.railnation_auth import authorize
from railnation.core.railnation_load import load_game


class Game(object):
    def __init__(self):
        log.info('Main object created.')

        client = Client()
        log.info('Client created.')

        print('Authorizing on rail-nation.com...')
        authorize(client)
        log.info('Authorization complete.')
        exit(0)
        print('Loading game parameters...')
        load_game(client)
        log.info('All preparations done.')

        self.screen = Screen()
        log.info('Screen ready.')

    def start(self):
        log.info('Game is starting!')
        while True:
            self.screen.update()
            time.sleep(0.1)

    def end(self):
        self.screen.end()
