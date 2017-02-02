#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import datetime

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.errors import RailNationInitializationError
from railnation.managers.resources import ResourcesManager
from railnation.managers.tina import TinaManager


class AvatarManager:
    """
    Representation of Rail-Nation player`s game avatar (game world main instance).
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: AvatarManager
        """
        if AvatarManager.instance is None:
            AvatarManager.instance = AvatarManager()

        return AvatarManager.instance

    def __init__(self):
        self.log = log.getChild('AvatarManager')
        self.id = None
        self.association_id = None
        self.player_names = {}
        self.premium_features = {
            'plus_ends_at': datetime.datetime.now()
        }
        self.era_number = None
        self.era_ends_at = None

    @property
    def era(self):
        if self.era_number is None or self.era_ends_at is None:
            self._update_era()
        elif self.era_ends_at < datetime.datetime.now():
            self._update_era()
            self.log.info('New era started: %s' % self.era_number)
        return self.era_number

    def _update_era(self):
        r = server.call('EraInterface', 'getEraInfos', [])
        now = datetime.datetime.now()
        self.era_number = r['Era']
        self.era_ends_at = now + datetime.timedelta(seconds=int(r['RemainingDuration']))

    def init(self, key):
        self.log.debug('Initializing...')

        self.id = server.call('AccountInterface', 'isLoggedIn', [key])
        if not self.id:
            raise RailNationInitializationError('Avatar in not logged in.')
        self.log.debug('Player ID: %s' % self.id)

        self._update_era()

        r = server.call('GUIInterface', 'getInitial', [])
        now = datetime.datetime.now()

        resources = ResourcesManager.get_instance()
        resources.resources = {int(i['resourceId']): int(i['amount']) for i in r['resources']}
        resources.limits = {int(i['resourceId']): int(i['limit']) for i in r['resources']}

        try:
            self.association_id = r['corporation']['ID']
        except KeyError:
            pass

        for i in r['paymentAccounts']:
            if i['type'] == '0':
                self.premium_features['plus_ends_at'] = now + datetime.timedelta(seconds=int(i['endTime']))
                self.log.debug('Plus active. End: %s' % self.premium_features['plus_ends_at'])

    @property
    def has_plus(self):
        return self.premium_features['plus_ends_at'] > datetime.datetime.now()


    def get_name(self, player_id):
        try:
            return self.player_names[player_id]
        except KeyError:
            player = server.call('ProfileInterface', 'getProfile', [player_id])
            self.player_names[player_id] = player['meta']['name']
            return self.player_names[player_id]