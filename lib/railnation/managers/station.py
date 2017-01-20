#!/usr/bin/env python
# -*- coding:  utf-8 -*-

from railnation.core.common import log


class StationManager:
    """
    Representation of Rail-Nation player`s station.

    """

    instance = None

    @staticmethod
    def get_instance():
        if StationManager.instance is None:
            StationManager.instance = StationManager()

        return StationManager.instance

    def __init__(self):
        self.log = log.getChild('StationManager')
        self.log.debug('Initializing...')


