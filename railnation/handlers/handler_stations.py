# -*- coding:utf-8 -*-
"""docstring"""
from railnation.core.railnation_log import log
log.debug('Loading Handler: Stations')

from railnation.core.railnation_globals import (
    screen,
    self_id,
)
from railnation.core.railnation_screen import Page
from railnation.core.railnation_models import Station


class Handler:
    name = 'stations'
    key = 'S'
    menu = 'See Stations'

    def __init__(self):
        self.page = StationPage(self_id)

    def loop(self):
        self.page.refresh()
        while True:
            screen.display_page(self.page)
            screen.communicate()


class StationPage(Page):
    def __init__(self, player_id):
        Page.__init__(self)
        self.station = Station(player_id)

    def refresh(self):
        self.station.update()
        self.layout = [
            (3, 15, 'This is a station of player: %s' % self.station.owner_id)
        ]
        for position, building in enumerate(self.station):
            self.layout.append((5 + position*2, 10, 'Type: %s' % building.type))
            self.layout.append((6 + position*2, 20, 'Level=%s Effects=%s Upgrade:$$%s Upgrade Effects=%s' %
                (building.level, building.effects,
                 building.money_to_upgrade, building.effects_next)))