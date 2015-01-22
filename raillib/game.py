# -*- coding:utf-8 -*-

from raillib.errors import NotAuthenticated

from raillib.client import Client

from raillib.map import global_map

from raillib.models import (
    Player,
    Town,
    Train,
    Station,
)


class Game(object):
    """
    Game object is needed to access your avatars and login to the game.
    """
    def __init__(self):
        self.client = Client()

    def authenticate(self, login, password):
        self.client.authenticate(login, password)

    def get_worlds(self):
        return self.client.get_worlds()

    def enter_world(self, world_id):
        if self.client.enter_world(world_id):
            return Avatar(self.client)
        else:
            return None


class Avatar(object):
    """
    Avatar object is access point to game methods and objects.
    """
    def __init__(self, client):
        self.client = client
        self.client.session.headers.update({'content-type': 'application/json'})

        self.player_id = 'False'
        self.properties = {}
        self.client_info = {}
        self.language = ''

        self._load_parameters()

    def _load_parameters(self):
        self.player_id = str(self.client.produce('AccountInterface',
                             'is_logged_in',
                             [self.client.webkey])['Body'])

        if self.player_id == 'False':
            raise NotAuthenticated('Error while getting your player_id.')

        r = self.client.produce('PropertiesInterface',
                                'getData',
                                [])['Body']

        self.properties = r['properties']
        self.properties['client'] = r['client']

        self.client_info = self.client.produce('KontagentInterface',
                                               'getData',
                                               [])['Body']

        self.language = str(self.client.produce('AccountInterface',
                                                'getLanguage',
                                                [])['Body'])

        self.map = None

    @property
    def yourself(self):
        return Player(self.client, self.player_id)

    @property
    def my_trains(self):
        return [Train(self.client, t)
                for t in self.client.produce('TrainInterface', 'getMyTrains',
                                             [True])['Body']]

    def get_station(self, owner_id=None):
        if owner_id is None:
            return Station(self.client, self.player_id)
        else:
            return Station(self.client, owner_id)

    def grab_ticket(self):
        pass