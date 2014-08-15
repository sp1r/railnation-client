# -*- coding:utf-8 -*-
"""Welcome!"""

from railnation.core.railnation_client import client
from railnation.screen.railnation_menu import menu
from railnation.pages.railnation_page import BasicPage


class Page(BasicPage):
    name = 'welcome'
    desc = 'Welcome page'
    key = 'W'

    def __init__(self):
        BasicPage.__init__(self)
        r = client.produce('WelcomeInterface',
                           'get',
                           [])['Body']
        self.layout.append((3, 15, 'Welcome to the game!'))
        self.layout.append((5, 10, 'Current Era is %d' % (r['currentEra'] + 1)))
        self.layout.append((6, 10, 'Era progress: %5.2f%%' % r['eraProgress']))
        self.layout.append((7, 10, 'Your rank now = %s' % r['userRank']))
        self.layout.append((8, 10, 'Trains needs repairing : %s' % r['lowReliableTrains']))
        self.layout.append((9, 10, 'Research points        : %s' % r['researchPoints']))
        self.layout.append((10, 10, 'Free rails             : %s' % r['leftRails']))
        self.layout.append((11, 10, 'Can buy trains         : %s' % r['leftTrains']))
        self.layout.append((12, 10, 'Free ticket ready      : %s' % r['lottery']['freeSlot']))
        self.layout.append((13, 10, 'Can buy workers        : %s' % r['numFreePersonalitySlots']))
