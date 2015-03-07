# -*- coding:utf-8 -*-
"""Модели используют client для доступа к игре"""


class Player:
    def __init__(self, client, player_id):
        self.client = client

        self.id = player_id

        self.params = {}
        self.corp_id = ''
        self.corp_name = ''
        self.corp_title = ''
        self.name = ''
        self.prestige = ''
        self.rank = ''
        self.total_trains = ''
        self.profit_today = ''

        self.update()

    def update(self):
        data = self.client.produce('ProfileInterface',
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
            self.corp_name = data['corporation']['name']
            self.corp_title = data['corporation']['title']
        except KeyError:
            self.corp_id = ''
            self.corp_name = ''
            self.corp_title = ''
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
            return Corporation(self.client, self.corp_id)
        else:
            return None

    @property
    def station(self):
        return Station(self.client, self.id)

    @property
    def collectables(self):
        return self.station.collectables

    @property
    def trains(self):
        for t in self.client.produce('TrainInterface', 'getMyTrains',
                                     [True])['Body']:
            yield Train(self.client, t)


class Corporation:
    def __init__(self, client, corp_id):
        self.client = client

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
        data = self.client.produce('CorporationInterface',
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
        self.member_ids = [str(x['user_id']) for x in data['members']
                           if x['title'] != '3']

    @property
    def members(self):
        return [Player(self.client, member_id)
                for member_id in self.member_ids]

    @property
    def stations(self):
        # return [Station(self.client, member_id)
        #         for member_id in self.member_ids]
        for member_id in self.member_ids:
            yield Station(self.client, member_id)

    @property
    def collectables(self):
        # all_collectables = []
        for station in self.stations:
            # all_collectables += station.collectables
            for collectable in station.collectables:
                yield collectable
        # return all_collectables


class Station:
    def __init__(self, client, owner_id):
        self.client = client

        self.owner_id = owner_id

        self.buildings = {}

        self.update()

    def update(self):
        data = self.client.produce('BuildingsInterface',
                                   'getAll',
                                   [self.owner_id])['Body']
        self.buildings = {
            building_id: Building(self.client, self.owner_id, building_data)
            for building_id, building_data in data.items()
        }

    def __repr__(self):
        return "<Station of player: %s>" % self.owner_id

    def __getitem__(self, item):
        return self.buildings[item]

    def __iter__(self):
        return self.buildings.values().__iter__()

    @property
    def collectables(self):
        return [self.buildings[t] for t in ('9', '10', '11')]


class Building:
    def __init__(self, client, owner_id, data):
        self.client = client
        self.owner_id = owner_id
        self.type = data['type']
        self.level = int(data['level'])
        self.finished = data['finished']
        self.construction_time = int(data['constructionTime'])
        self.money_to_upgrade = -int(data['resourcesNext']['1'])
        self.prestige_for_next_level = int(data['resourcesNext']['3'])
        self.max_level = int(data['maxLevel'])
        self.effects = data['effects']
        self.effects_next = data['effectsNext']
        self.production_time = int(data['productionTime'])

    def __repr__(self):
        return "<Building level %d of type %d" % (self.level, self.type)

    @property
    def bonus_ready(self):
        if self.production_time == 0:
            return True
        else:
            return False

    def collect(self, direct=False):
        if direct:
            result = self.client.produce('BuildingsInterface',
                                         'collect',
                                         [self.type])
        else:
            result = self.client.produce('BuildingsInterface',
                                         'collect',
                                         [self.type, self.owner_id])

        if result["Errorcode"] == 10054:
            # Bank overflow
            return 10054, None
        elif not result["Body"]:
            # already collected
            return 1, None
        else:
            # success
            ticket = self.client.produce('LotteryInterface',
                                         'isForFree',
                                         [])
            if ticket['Body']['freeSlot']:
                self.client.produce('LotteryInterface', 'buy', [])
                return 0, self.client.produce('LotteryInterface',
                                              'rewardLottery',
                                              [])['Infos']
            else:
                return 0, None


class Town:
    def __init__(self, client, town_id):
        self.client = client

        self.id = town_id
        self.name = ''
        self.level = 0
        self.capacity = 0
        self.growth_floor = 0
        self.resources = {}
        self.update()

    def update(self):
        r = self.client.produce('TownInterface', 'getDetails', [self.id])['Body']
        self.name = r['town']['name']
        self.level = r['town']['level']

        self.capacity = int(r['resources'][0]['capacity'])
        self.growth_floor = int(self.capacity * 0.67)
        for res in r['resources']:
            self.resources[int(res['resource_type'])] = {
                'amount': int(res['amount']),
                'consume': int(res['consume_amount']),
                'price': int(res['price']),
                'price_factor': float(res['price_factor']),
                'priority': int(res['priority']),
                'trend': float(res['trend']),
            }

    # @property
    # def growth(self):
    #     g = 0.0
    #     for good in self.resources.values():
    #         if good['priority'] == 1:
    #             g += 25.0 * min(1.0, (good['amount'] - good['consume'])/self.growth_floor)
    #     return g


class Train:
    def __init__(self, client, data):
        self.client = client

        self.id = data['ID']
        self.owner_id = data['user_id']
        self.name = data['name']
        self.type = data['type']

        self.reliability = data['reliability']
        self.maintenance_costs = data['maintenance_costs']
        self.profit_today = data['profit_today']
        self.profit_last_hour = data['profit_last_hour']

        self.boost_end = data['boost_end']
        self.mechanic_end = data['mechanic_end']
        self.bought = data['bought']

        self.profit = data['profit']
        self.costs_today = data['costs_today']

        self.max_num_waggons_base = data['max_num_waggons_base']
        self.endurance = data['endurance']
        self.tech_id = data['tech_id']

        self.waggons = data['waggons']
        self.upgrades = [x['id'] for x in data['upgrades']]

        self.navigation = data['navigation']

        self.value = data['value']

    def update_navigation(self):
        self.navigation = \
            self.client.produce('TrainInterface', 'getTrack',
                                [self.id, True, False])['Body']

    def repair(self):
        return self.client.produce('TrainInterface', 'doMaintenance',
                                   [self.id])['Body']

    def get_schedule(self):
        response = self.client.produce('TrainInterface', 'getRoadMap',
                                       [self.id])
        schedule = Schedule()
        for item in response['Body']:
            schedule.append_target(item['location_id'])
            schedule.elements[-1].loading = item['loading']
        return schedule

    def set_schedule(self, schedule):
        assert isinstance(schedule, Schedule)
        road_map = []
        for element in schedule.elements:
            road_map.append({
                'dest_id': element.id,
                'scheduleType': int(element.temporary) + 1,
                'wait': element.wait_type,
                'loading': element.loading,
            })

        response = self.client.produce('TrainInterface', 'setRoadMap',
                                       [self.id, road_map])

    def __repr__(self):
        return '<Train %s with ID=%s>' % (self.type, self.id)

    def __lt__(self, other):
        if int(self.bought) != int(other.bought):
            return int(self.bought) < int(other.bought)

        else:
            return self.id < other.id

    def __eq__(self, other):
        return not self < other and not other < self

    def __ne__(self, other):
        return self < other or other < self

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self


class Schedule(object):
    def __init__(self):
        self.elements = []

    def clear(self):
        self.elements = []

    def append_temporary(self, location_id):
        self.elements.append(Element(location_id,
                                     is_temporary=True))

    def append_passing_by(self, location_id):
        self.elements.append(Element(location_id))

    def append_target(self, location_id):
        self.elements.append(Element(location_id,
                                     is_temporary=False,
                                     pass_by=False))

    def load(self, waggon_type, amount):
        loading_rule = {
            'type': waggon_type,
            'load': amount,
            'unload': 0,
        }
        self.elements[-1].add_loading_rule(loading_rule)

    def unload(self, waggon_type, amount):
        loading_rule = {
            'type': waggon_type,
            'load': 0,
            'unload': amount,
        }
        self.elements[-1].add_loading_rule(loading_rule)


class Element(object):
    def __init__(self, location_id, is_temporary=False, pass_by=True):
        self.id = location_id
        self.temporary = is_temporary
        self.pass_by = pass_by
        self.load_here = False
        self.loading = []

    def add_loading_rule(self, rule):
        if rule['load'] != 0:
            self.load_here = True
        self.loading.append(rule)

    @property
    def wait_type(self):
        if self.pass_by:
            return -1
        elif self.load_here:
            return 60
        else:
            return 0