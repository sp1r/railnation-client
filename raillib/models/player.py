# -*- coding: utf-8 -*-
__author__ = 'sp1r'

from core import client
from core.base import config
import models


class Player:
    def __init__(self, pid):
        self.id = pid
        self.name = ""
        self.corp_id = ""
        self.prestige = 0
        self.total_trains = 0
        self.profit_today = 0

        # load initial values
        self.update()

    def __repr__(self):
        return "Name: %s\nId: %s\nPrestige: %s" % (self.name, self.id, str(self.prestige))

    def update(self):
        data = client.get_user(self.id)
        data = data['Body']
        self.name = data['username']
        self.id = str(data['user_id'])
        self.corp_id = str(data['corporation']['ID'])
        self.prestige = int(data['prestige'])
        self.total_trains = data['amountOfTrains']
        self.profit_today = data['salesToday']

    def get_corporation(self):
        if self.corp_id:
            return models.Corporation(self.corp_id)
        else:
            return None

    def get_station(self):
        return models.Station(self.id)

    def trains(self):
        if self.id == config['self_id']:
            data = client.get_my_trains()
        else:
            data = client.get_trains(self.id)
        for train in data['Body']:
            yield models.Train(train['ID'])

    def get_trains_list(self):
        if self.id == config['self_id']:
            data = client.get_my_trains()
        else:
            data = client.get_trains(self.id)
        trains = []
        for train in data['Body']:
            trains.append(models.Train(train['ID']))
        return trains