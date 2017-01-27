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
    Representation of Rail-Nation player`s station.
    """

    instances = {}

    @staticmethod
    def get_instance(player_id=None):
        if player_id is None:
            player_id = AvatarManager.get_instance().id

        try:
            return StationManager.instances[player_id]
        except KeyError:
            StationManager.instances[player_id] = StationManager(player_id)
            return StationManager.instances[player_id]

    def __init__(self, player_id):
        self.log = log.getChild('StationManager')
        self.log.debug('Initializing player station: %s' % player_id)
        self.player_id = player_id
        self.buildings = {i: {} for i in range(10)}

        self.update_all_buildings()

    def update_all_buildings(self):
        r = server.call('BuildingInterface', 'getBuildings', [self.player_id])
        for b in r:
            self.update_building(b)

    def update_building(self, building_data):
        now = datetime.datetime.now()
        building = {
            'name': building_names[int(building_data['type'])],
            'level': int(building_data['level']),
            'build_in_progress': int(building_data['hasUpgraded']) == 0,
            'build_finish_at': now + datetime.timedelta(seconds=int(building_data['durationLeft']) + int(building_data['lastDurationUpdate'])),
            'production_at': now + datetime.timedelta(seconds=int(building_data['productionTimeLeft']) + int(building_data['lastProductionUpdate'])),
            'video_watched': int(building_data['hasWatched']) == 1,
        }
        debug_msg = '%(name)s level=%(level)s build_in_progress=%(build_in_progress)s '
        if building['build_in_progress']:
            debug_msg += 'build_finish_at=%(build_finish_at)s '
        if int(building_data['type']) in (7, 8, 9):
            debug_msg += 'production_at=%(production_at)s video_watched=%(video_watched)s '
        self.log.debug(debug_msg % building)
        self.buildings[int(building_data['type'])] = building

