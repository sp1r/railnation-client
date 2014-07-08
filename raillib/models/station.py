# -*- coding: utf-8 -*-
__author__ = 'spir'

from core import client
from core.base import config, log
import core.constants as const


class Station:
    def __init__(self, pid):
        self.owner = pid
        self.buildings = {}

        # load initial values
        self.update()

    def __repr__(self):
        return "Owner: %s\nDepots: %d\nLaba: %d" % (self.owner, self.buildings['3'].level, self.buildings['5'].level)

    def update(self):
        data = client.get_buildings(self.owner)
        data = data['Body']
        for key in data:
            self.buildings[int(key)] = Building(self.owner, data[key])

    def collectables(self):
        for t in (9, 10, 11):
            yield self.buildings[t]


class Building:
    def __init__(self, owner, data):
        self.owner = owner
        self.type = int(data['type'])
        self.level = int(data['level'])
        self.finished = data['finished']
        self.construction_time = data['constructionTime']
        self.requirements = data['resourcesNext']
        self.max_level = data['maxLevel']
        self.effects = data['effects']
        self.effects_next = data['effectsNext']
        self.production_time = data['productionTime']

    def __repr__(self):
        return "%d %d" % (self.type, self.level)

    def collect(self):
        log.debug('Collecting %s for player %s' % (const.buildings[self.type], self.owner))
        if self.owner == config['self_id']:
            result = client.collect_self(self.type)
        else:
            result = client.collect(self.owner, self.type)

        if result["Errorcode"] == 10054:
            log.info('%s: Bank overflow' % self.owner)
        elif not result["Body"]:
            log.info('%s: Missed' % self.owner)
        else:
            log.info('%s: Collected' % self.owner)
            ticket = client.check_lottery()
            if ticket['Body']['freeSlot']:
                log.info('Got ticket!' % self.owner)
                prize = client.collect_ticket()
                log.info('Prize: %s' % str(prize['Infos']))