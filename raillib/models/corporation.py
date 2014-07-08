__author__ = 'spir'

from core import client
import models


class Corporation:
    def __init__(self, corp_id):
        self.id = corp_id
        self.name = None
        self.description = None
        self.prestige = None
        self.level = None
        self.home_town = None
        self.members = []
        self.update()

    def update(self):
        data = client.get_corp(self.id)
        data = data['Body']
        self.name = data['name']
        self.id = str(data['ID'])
        self.prestige = float(data['prestige'])
        self.level = int(data['level'])
        self.home_town = str(data['homeTown'])
        self.members = []
        for user in data['members']:
            if user['title'] != '3':
                self.members.append(user['user_id'])

    def players(self):
        for player_id in self.members:
            yield models.Player(player_id)

    def stations(self):
        for player_id in self.members:
            yield models.Station(player_id)

    def collectables(self):
        for station in self.stations():
            for building in station.collectables():
                yield building