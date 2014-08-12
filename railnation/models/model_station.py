# -*- coding: utf-8 -*-

from railnation.core.railnation_globals import log


class Station():
    def __init__(self, client, owner_id, data):
        self.owner_id = owner_id
        self.buildings = {
            building_id: Building(client, owner_id, building_data)
            for building_id, building_data in data.items()
        }

    def __repr__(self):
        return "<Station of player: %s>" % self.owner_id

    @property
    def collectables(self):
        for t in (9, 10, 11):
            yield self.buildings[t]


class Building():
    def __init__(self, client, owner_id, data):
        self.owner_id = owner_id
        self.type = int(data['type'])
        self.level = int(data['level'])
        self.finished = data['finished']
        self.construction_time = int(data['constructionTime'])
        self.money_to_upgrade = -int(data['resourcesNext']['1'])
        self.prestige_for_next_level = int(data['resourcesNext']['3'])
        self.max_level = int(data['maxLevel'])
        self.effects = data['effects']
        self.effects_next = data['effectsNext']
        self.production_time = data['productionTime']

    def __repr__(self):
        return "<Building level %d of type %d" % (self.level, self.type)

    def collect(self):
        log.debug('Collecting %d for player %s' % (self.type, self.owner_id))
        result = self.client.collect(self.owner_id, self.type)

        if result["Errorcode"] == 10054:
            log.info('%s: Bank overflow' % self.owner_id)
        elif not result["Body"]:
            log.info('%s: Missed' % self.owner_id)
        else:
            log.info('%s: Collected' % self.owner_id)
            ticket = self.client.check_lottery()
            if ticket['Body']['freeSlot']:
                log.info('Got ticket!' % self.owner_id)
                prize = self.client.collect_ticket()
                log.info('Prize: %s' % str(prize['Infos']))