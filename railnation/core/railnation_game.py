# -*- coding:utf-8 -*-
"""docstring"""

import time

from railnation.core.railnation_globals import log
from railnation.core.railnation_client import Client
from railnation.core.railnation_auth import authorize
from railnation.core.railnation_screen import Screen

from railnation.models.railnation_model import Model


class Game(object):
    def __init__(self):
        log.info('Game is loading!')
        self.client = Client()
        authorize(self.client)

        if Model.client is None:
            Model.client = self.client

        self.screen = Screen()

    def start(self):
        while True:
            self.screen.update()
            time.sleep(0.1)

    def end(self):
        self.screen.end()
