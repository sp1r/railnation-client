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
        self.premium_features = {
            'plus_ends_at': datetime.datetime.now()
        }

    def init(self, key):
        self.log.debug('Initializing...')

        self.id = server.call('AccountInterface', 'isLoggedIn', [key])
        if not self.id:
            raise RailNationInitializationError('Avatar in not logged in.')
        self.log.debug('Player ID: %s' % self.id)

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

    @property
    def has_plus(self):
        return self.premium_features['plus_ends_at'] > datetime.datetime.now()

