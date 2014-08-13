# -*- coding:utf-8 -*-
"""Модели используют client для доступа к игре"""

from railnation.core.railnation_globals import log
from railnation.core.railnation_client import client


class Player():
    def __init__(self, player_id=None):

        if player_id is None:
            self.id = client.player_id
        else:
            self.id = player_id

        self.params = {}
        self.corp_id = ''
        self.name = ''
        self.prestige = ''
        self.rank = ''
        self.total_trains = ''
        self.profit_today = ''

        self.update()

    def update(self):
        data = client.produce('ProfileInterface',
                              'get_profile_data',
                              [self.id])['Body']
        self.id = str(data['user_id'])
        self.params = {
            'hometown_is_public': data['hometown_is_public'],
            'country_is_public': data['country_is_public'],
            'birthday_is_public': data['birthday_is_public'],
            'hometown': data['hometown'],
            'country': data['country'],
            'birthday': data['birthday'],
            'receive_newsletter': data['receive_newsletter'],
            'client_options': data['client_options'],
            'profile_text': data['profile_text'],
            'gender': data['gender'],
            'starting_town': data['startingTown'],
            'languages': data['selectableLanguages'],
            'meta': data['meta'],
        }
        try:
            self.corp_id = str(data['corporation']['ID'])
        except KeyError:
            pass
        self.name = data['username']
        self.prestige = data['prestige']
        self.rank = data['highscore_rank']
        self.total_trains = data['amountOfTrains']
        self.profit_today = data['salesToday']

    def __repr__(self):
        return "<Player %s with id: %s>" % (self.name, self.id)

    @property
    def corporation(self):
        if self.corp_id:
            return Corporation(self.corp_id)
        else:
            return None

    @property
    def station(self):
        return Station(self.id)


class Corporation():
    def __init__(self, corp_id):
        self.id = corp_id

        self.name = ''
        self.description = ''
        self.image = {}
        self.foundation_date = ''
        self.prestige = ''
        self.level = ''
        self.home_town = ''
        self.country = ''
        self.member_ids = []

        self.update()

    def update(self):
        data = client.produce('CorporationInterface',
                                    'get',
                                    [self.id])['Body']
        self.name = data['name']
        self.description = data['description']
        self.image = {
            'background': data['background'],
            'pattern': data['pattern'],
            'emblem': data['emblem'],
            'color1': data['color1'],
            'color2': data['color2'],
            'color3': data['color3'],
            #'base64': data['image'],  # what for do we need this png-image?
        }
        self.foundation_date = data['foundationDate']
        self.prestige = data['prestige']
        self.level = data['level']
        self.home_town = data['homeTown']
        self.country = data['country']
        self.member_ids = [str(x['user_id']) for x in data['members']]

    @property
    def members(self):
        for member_id in self.member_ids:
            yield Player(member_id)

    @property
    def stations(self):
        for member_id in self.member_ids:
            yield Station(member_id)

    @property
    def collectables(self):
        for station in self.stations:
            for building in station.collectables:
                yield building


class Station():
    def __init__(self, owner_id):
        self.owner_id = owner_id

        self.buildings = {}

        self.update()

    def update(self):
        data = client.produce('BuildingsInterface',
                                    'getAll',
                                    [self.owner_id])['Body']
        self.buildings = {
            building_id: Building(self.owner_id, building_data)
            for building_id, building_data in data.items()
        }

    def __repr__(self):
        return "<Station of player: %s>" % self.owner_id

    @property
    def collectables(self):
        for t in (9, 10, 11):
            yield self.buildings[t]


class Building():
    def __init__(self, owner_id, data):
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

    # def collect(self):
    #     log.debug('Collecting %d for player %s' % (self.type, self.owner_id))
    #     result = Model.client.collect(self.owner_id, self.type)
    #
    #     if result["Errorcode"] == 10054:
    #         log.info('%s: Bank overflow' % self.owner_id)
    #     elif not result["Body"]:
    #         log.info('%s: Missed' % self.owner_id)
    #     else:
    #         log.info('%s: Collected' % self.owner_id)
    #         ticket = self.client.check_lottery()
    #         if ticket['Body']['freeSlot']:
    #             log.info('Got ticket!' % self.owner_id)
    #             prize = self.client.collect_ticket()
    #             log.info('Prize: %s' % str(prize['Infos']))