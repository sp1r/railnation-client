#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import datetime

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.const import building_names
from railnation.managers.avatar import AvatarManager
from railnation.core.errors import RailNationClientError


class StationManager:
    """
    Manager of Rail-Nation player stations.
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: StationManager
        """
        if StationManager.instance is None:
            StationManager.instance = StationManager()
        return StationManager.instance

    def __init__(self):
        self.log = log.getChild('StationManager')
        self.log.debug('Initializing...')

    def get_buildings(self, player_id):
        if player_id is None:
            player_id = AvatarManager.get_instance().id

        self.log.debug('Constructing station of player: %s' % player_id)

        r = server.call('BuildingInterface', 'getBuildings', [player_id])
        now = datetime.datetime.now()
        station = {}
        for b in r:
            station[int(b['type'])] = {
                'name': building_names[int(b['type'])],
                'level': int(b['level']),
                'build_in_progress': int(b['hasUpgraded']) == 0,
                'build_finish_at': now + datetime.timedelta(
                    seconds=int(b['durationLeft']) + int(b['lastDurationUpdate'])),
                'production_at': now + datetime.timedelta(
                    seconds=int(b['productionTimeLeft']) + int(b['lastProductionUpdate'])),
                'video_watched': int(b['hasWatched']) == 1,
            }
            debug_msg = '%(name)s level=%(level)s build_in_progress=%(build_in_progress)s '
            if station[int(b['type'])]['build_in_progress']:
                debug_msg += 'build_finish_at=%(build_finish_at)s '
            if int(b['type']) in (7, 8, 9):
                debug_msg += 'production_at=%(production_at)s video_watched=%(video_watched)s '
            self.log.debug(debug_msg % station[int(b['type'])])
        return station

