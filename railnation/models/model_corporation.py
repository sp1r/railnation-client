#-*- encoding: utf-8 -*-

"""Корпорация"""

from railnation.core.railnation_globals import client


class Corporation:
    def __init__(self, data):
        self.id = str(data['ID'])
        self.name = data['name']
        self.description = data['description']
        self.image = {
            'background': data['background'],
            'pattern': data['pattern'],
            'emblem': data['emblem'],
            'color1': data['color1'],
            'color2': data['color2'],
            'color3': data['color3'],
            'base64': data['image'],
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
            yield client.get_user(member_id)

    @property
    def stations(self):
        for member_id in self.member_ids:
            yield client.get_station(member_id)

    @property
    def collectables(self):
        for station in self.stations:
            for building in station.collectables:
                yield building