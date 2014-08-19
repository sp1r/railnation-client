# -*- coding:utf-8 -*-
"""docstring"""

from railnation.core.railnation_globals import (
    client,
    screen,
)
from railnation.core.railnation_screen import Page


class Handler:
    name = 'welcome'
    key = 'W'

    def __init__(self):
        self.page = WelcomePage()

    def loop(self):
        while True:
            screen.display_page(self.page)
            screen.communicate()


class WelcomePage(Page):
    def __init__(self):
        Page.__init__(self)

    def refresh(self):
        r = client.produce('WelcomeInterface',
                           'get',
                           [])['Body']
        self.layout = (
            (3, 15, 'Welcome to the game!'),
            (5, 10, 'Current Era            : %d' % (r['currentEra'] + 1)),
            (6, 10, 'Era progress           : %5.2f%%' % r['eraProgress']),
            (7, 10, 'Your rank now          : %s' % r['userRank']),
            (8, 10, 'Trains needs repairing : %s' % r['lowReliableTrains']),
            (9, 10, 'Research points        : %s' % r['researchPoints']),
            (10, 10, 'Free rails             : %s' % r['leftRails']),
            (11, 10, 'Can buy trains         : %s' % r['leftTrains']),
            (12, 10, 'Free ticket ready      : %s' % r['lottery']['freeSlot']),
            (13, 10, 'Can buy workers        : %s' % r['numFreePersonalitySlots']),
        )

        self.help_lines = (
            '"a" - Account settings',
            '"w" - go back on welcome screen',
        )