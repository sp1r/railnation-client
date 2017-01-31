#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import cherrypy
from cherrypy.process.plugins import Monitor

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.errors import RailNationClientError


class TinaManager:
    """
    Mystical "Tina" manager.
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: TrainsManager
        """
        if TinaManager.instance is None:
            TinaManager.instance = TinaManager()

        return TinaManager.instance

    def __init__(self):
        self.log = log.getChild('TinaManager')
        self.log.debug('Initializing...')

    def refresh(self):
        self.log.debug('Refresh threads')
        if server.api_url is None:
            self.log.debug('Game not initialized! Skipping refresh.')
            return

        r = server.call('TinaInterface', 'getThreads', [])
        self.log.debug('Result: %s' % r)


Monitor(cherrypy.engine, TinaManager.get_instance().refresh, frequency=60, name='TinaMonitor').subscribe()

