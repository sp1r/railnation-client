#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import cherrypy
from cherrypy.process.plugins import Monitor

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.errors import RailNationClientError
from railnation.managers.properties import PropertiesManager


upgrade_types = {
    '1': 'waggons',
    '2': 'speed',
    '3': 'endurance',
    '4': 'acceleration',
    '5': 'coupling',
}


class TrainsManager:
    """
    Trains manager.
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: TrainsManager
        """
        if TrainsManager.instance is None:
            TrainsManager.instance = TrainsManager()

        return TrainsManager.instance

    def __init__(self):
        self.log = log.getChild('TrainsManager')
        self.log.debug('Initializing...')
        self.train_types = {}
        self.train_upgrades = {}

    def load_train_types(self):
        self.log.debug('Loading trains data')
        raw_trains = PropertiesManager.get_instance().get_trains()
        for train in raw_trains:
            self.train_types[train['ID']] = {
                'speed': int(train['speed']),
                'acc': int(train['acc']),
                'endurance': int(train['endurance']),
                'price': int(train['price']),
                'waggons': int(train['max_num_waggons']),
                'slots': int(train['train_slots']),
                'category': train['train_category'],
                'passenger': train['isPassengerTrain'],
                'order_id': train['order_id'],
            }
        self.log.debug('Loaded %s train types' % len(self.train_types))

    def load_train_upgrades(self):
        self.log.debug('Loading train upgrades')
        raw_upgrades = PropertiesManager.get_instance().get_train_upgrades()
        for upgrade in raw_upgrades:
            self.train_upgrades[upgrade['ID']] = {
                'type': upgrade['type'],
                'type_string': upgrade_types[upgrade['type']],
                'effect': int(upgrade['effect']),
                'effect_string': '%s +%s' % (upgrade_types[upgrade['type']], upgrade['effect']),
                'cost': int(upgrade['cost']),
            }
        self.log.debug('Loaded %s train upgrades' % len(self.train_upgrades))

    def refresh(self):
        pass


Monitor(cherrypy.engine, TrainsManager.get_instance().refresh, frequency=10, name='TrainsMonitor').subscribe()

