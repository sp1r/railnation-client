#!/usr/bin/env python
# -*- coding:  utf-8 -*-

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.errors import RailNationInitializationError


class AvatarManager:
    """
    Representation of Rail-Nation player`s game avatar (game world main instance).

    """

    instance = None

    @staticmethod
    def get_instance():
        if AvatarManager.instance is None:
            AvatarManager.instance = AvatarManager()

        return AvatarManager.instance

    def __init__(self):
        self.log = log.getChild('AvatarManager')
        self.log.debug('Initializing...')
        self.id = server.call('AccountInterface', 'isLoggedIn', [])
        if not self.id:
            raise RailNationInitializationError('Avatar in not logged in.')


