#!/usr/bin/env python
# -*- coding:  utf-8 -*-

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.errors import RailNationClientError


class TicketManager:
    """
    Lottery ticket opener.
    """

    instance = None

    @staticmethod
    def get_instance():
        if TicketManager.instance is None:
            TicketManager.instance = TicketManager()

        return TicketManager.instance

    def __init__(self):
        self.log = log.getChild('TicketManager')
        self.log.debug('Initializing...')
        self.auto_open = False
        self.stats = {}
        self.history = []

    def open(self):
        self.log.debug('Check for free tickets')
        r = server.call(
            'LotteryInterface',
            'getScreen',
            []
        )
        self.log.debug('Lottery info: %s' % r)
        if r['freeUsages'] == 0:
            error_msg = 'No free tickets! Use "buy" method instead.'
            self.log.error(error_msg)
            raise RailNationClientError(error_msg)

        self.log.debug('Opening lottery ticket')
        reward = server.call(
            'LotteryInterface',
            'playPackage',
            [-1]  # ???
        )
        self.log.debug('Reward: %s' % reward)
        self.log.debug('Claiming reward...')
        r = server.call(
            'LotteryInterface',
            'redeem',
            []
        )
        if not r:
            self.log.error('Reward not redeemed: %s' % r)

        else:
            self.log.info('Opened ticket. Got: %s' % reward)



