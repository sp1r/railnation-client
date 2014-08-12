# -*- coding: utf-8 -*-
"""Игрок railnation"""

from railnation.models.railnation_model import Model


class Player(Model):
    def __init__(self, data):
        Model.__init__(self)
        self._parse_data(data)

    def _parse_data(self, data):
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
            self.corp_id = ''
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
            return Model.client.get_corp(self.corp_id)
        else:
            return None

    @property
    def station(self):
        return Model.client.get_station(self.id)

    # def trains(self):
    #     if self.id == config['self_id']:
    #         data = client.get_my_trains()
    #     else:
    #         data = client.get_trains(self.id)
    #     for train in data['Body']:
    #         yield models.Train(train['ID'])
    #
    # def get_trains_list(self):
    #     if self.id == config['self_id']:
    #         data = client.get_my_trains()
    #     else:
    #         data = client.get_trains(self.id)
    #     trains = []
    #     for train in data['Body']:
    #         trains.append(models.Train(train['ID']))
    #     return trains