# -*- coding:utf-8 -*-
"""docstring"""

import time

import railnation.core.railnation_globals as global_vars

from railnation.core.railnation_screen import Screen
from railnation.core.railnation_client import Client
from railnation.core.railnation_auth import authorize


class Game(object):
    def __init__(self):
        global_vars.log.info('Game is starting!')
        # client = Client()
        # authorize(client)
        # global_vars.client = client

        self.screen = Screen()

    def start(self):
        while True:
            self.screen.update()
            time.sleep(0.1)

    def end(self):
        self.screen.end()
