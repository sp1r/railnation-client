# -*- coding:utf-8 -*-
"""docstring"""

from railnation.pages.railnation_page import BasicPage
from railnation.core.railnation_models import Player


class Page(BasicPage):
    def __init__(self):
        BasicPage.__init__(self)
        self.layout = [(0, 0, 'This is player profile page.'),
                       (1, 0, 'Currently in development...')]
        self.switch_key = 'P'


class Dummy:
    def __init__(self):
        self.name = 'Dr. Frankenstein'
        self.corp = 'Корпорация Я'
        self.rank = 1324
        self.total_trains = 12
        self.profit_today = 12341234
        self.money = 50000000
        self.prestige = 1234567
        self.gold = 15000


from railnation.core.railnation_models import Player


def get_page(player_id=None):
    #player = Player(player_id)
    player = Dummy()

    layout = [
        (1, 1, 'Player      : %s' % player.name),
        (2, 1, 'Corporation : %s' % player.corp),
        (3, 1, 'Prestige    : %s' % player.prestige),
        (4, 1, 'Rank        : %s' % player.rank),
        (5, 1, 'Trains      : %s' % player.total_trains),
        (6, 1, '$$ today    : %s' % player.profit_today),
    ]

    navigation_zones = []

    controls = {}

    return layout, navigation_zones, controls