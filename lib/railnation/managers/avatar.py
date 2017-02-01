#!/usr/bin/env python
# -*- coding:  utf-8 -*-

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

    def init(self, key):
        self.log.debug('Initializing...')

        self.id = server.call('AccountInterface', 'isLoggedIn', [key])
        if not self.id:
            raise RailNationInitializationError('Avatar in not logged in.')
        self.log.debug('Player ID: %s' % self.id)

        r = server.call('GUIInterface', 'getInitial', [])

        resources = ResourcesManager.get_instance()
        resources.resources = {int(i['resourceId']): int(i['amount']) for i in r['resources']}
        resources.limits = {int(i['resourceId']): int(i['limit']) for i in r['resources']}

        try:
            self.association_id = r['corporation']['ID']
        except KeyError:
            pass

    def get_name(self, player_id):
        try:
            return self.player_names[player_id]
        except KeyError:
            player = server.call('ProfileInterface', 'getProfile', [player_id])
            self.player_names[player_id] = player['meta']['name']
            return self.player_names[player_id]