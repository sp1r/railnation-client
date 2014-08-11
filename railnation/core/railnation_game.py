# -*- coding:utf-8 -*-
"""docstring"""

from railnation.core.railnation_globals import client
from railnation.core.railnation_auth import authorize_client


class Game(object):
    def __init__(self):
        authorize_client(client)

    def start(self):
        while True:
            pass

    def end(self):
        return
