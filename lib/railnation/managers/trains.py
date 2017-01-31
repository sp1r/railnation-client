#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import cherrypy
from cherrypy.process.plugins import Monitor

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.errors import RailNationClientError


class TrainsManager:
    """
    Trains manager.
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: TrainsManager
        """
        if TrainsManager.instance is None:
            TrainsManager.instance = TrainsManager()

        return TrainsManager.instance

    def __init__(self):
        self.log = log.getChild('TrainsManager')
        self.log.debug('Initializing...')

    def refresh(self):
        pass


Monitor(cherrypy.engine, TrainsManager.get_instance().refresh, frequency=10, name='TrainsMonitor').subscribe()

