# -*- coding:utf-8 -*-
"""Info section data management"""

from time import time

from railnation.core.railnation_client import client
from railnation.core.railnation_models import Player


example_infos = (
    'Name: Dr. Frankenstein',
    'Copr: Газетчики',
    'Prestige: 1 234 567',
    'Rank: 12 343',
    'Money: 50 000 000',
    'Gold: 15 000'
)


class InfoContainer:
    def __init__(self):
        self.infos = ()
        self.last_refresh = 0.0
        self.refresh_period = 120.0

    def get_infos(self):
        if time() - self.last_refresh > self.refresh_period:
            self.refresh()
        return self.infos

    def refresh(self):
        self.last_refresh = time()


class ResourceContainer(InfoContainer):
    """Занимается учетом ресурсов"""
    def __init__(self):
        InfoContainer.__init__(self)
        self.resources = {}
        self.player = Player()

    def store(self, resource, amount):
        self.resources[resource] += amount
        self._update_infos()

    def take(self, resource, amount):
        if self.resources[resource] >= amount:
            self.resources[resource] -= amount
            self._update_infos()
            return True
        else:
            return False

    def refresh(self):
        self.last_refresh = time()
        self.player.update()
        r = client.produce('GUIInterface',
                           'get_gui',
                           [])
        for res_id, data in r['Body']['resources'].items():
            self.resources[int(res_id)] = int(data['amount'])
        self._update_infos()

    def _update_infos(self):
        self.infos = (
            'Name: %s' % self.player.name,
            'Copr: %s' % self.player.corp_name,
            'Prestige: %s' % self.resources[3],
            'Rank: %s' % self.player.rank,
            'Money: %s' % self.resources[1],
            'Gold: %s' % self.resources[2],
        )

info = ResourceContainer()