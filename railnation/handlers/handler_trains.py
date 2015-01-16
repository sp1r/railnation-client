# -*- coding:utf-8 -*-
"""docstring"""

from railnation.core.railnation_handler import HandlerBase


class Handler(HandlerBase):
    name = 'trains'

    def __init__(self, client):
        HandlerBase.__init__(self, client)

    def execute(self, command):
        pass

    def show(self):
        return 'trains handler show'

    def help(self):
        return 'trains handler help'