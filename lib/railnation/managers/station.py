#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import datetime
import cherrypy
from cherrypy.process.plugins import Monitor

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.const import building_names
from railnation.managers.avatar import AvatarManager
from railnation.managers.properties import PropertiesManager
from railnation.managers.resources import ResourcesManager
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
        self.build_queue = []

    def get_buildings(self, player_id=None):
        if player_id is None:
            player_id = AvatarManager.get_instance().id

        self.log.debug('Constructing station of player: %s' % player_id)

        r = server.call('BuildingInterface', 'getBuildings', [player_id])
        now = datetime.datetime.now()
        station = {}
        for b in r:
            station[int(b['type'])] = {
                'name': PropertiesManager.get_instance().buildings[int(b['type'])]['name'],
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

    def upgrade_building(self, building_id):
        building_id = int(building_id)
        self.build_queue.append(building_id)
        self.check_build_queue()

    def check_build_queue(self):
        if len(self.build_queue) == 0:
            return

        buildings = StationManager.get_instance().get_buildings()

        build_tasks = [x for x in buildings.values() if x['build_in_progress']]
        self.log.debug('Build tasks count: %s' % len(build_tasks))

        max_builders = 2 if AvatarManager.get_instance().has_plus else 1
        self.log.debug('Max builders: %s' % max_builders)

        if len(build_tasks) >= max_builders:
            self.log.debug('No build slot available. Waiting...')
            return

        building_id = self.build_queue[0]
        building_name = PropertiesManager.get_instance().buildings[building_id]['name']
        building = buildings[building_id]

        if building['build_in_progress']:
            self.log.debug('%s is currently being upgraded, will start upgrade after current one is finished.' %
                           building_name)
            return

        upgrade_requirements = PropertiesManager.get_instance().buildings[building_id]['levels'][str(building['level'] + 1)]['conditions']
        upgrade_cost = None
        upgrade_era = 1
        for i in upgrade_requirements:
            if i['function'] == 'Resources.getResource':
                upgrade_cost = i['compare']['>=']
            elif i['function'] == 'Era.getCurrentEra':
                upgrade_era = int(i['compare']['>=']) + 2
        if upgrade_era > AvatarManager.get_instance().era:
            self.log.warning('Cannot upgrade %s. Required era: %s. Current era: %s' %
                             (building_name,
                              upgrade_era,
                              AvatarManager.get_instance().era))
            self.build_queue = self.build_queue[1:]
            return

        if not ResourcesManager.get_instance().have_enough_money(upgrade_cost):
            self.log.debug('There is not enough money to upgrade %s now. Waiting...' % building_name)
            return

        self.log.info('Starting upgrade of %s to level %s' %
                      (building_name, building['level'] + 1))
        r = server.call('BuildingInterface', 'build', [building_id])
        self.build_queue = self.build_queue[1:]


Monitor(cherrypy.engine, StationManager.get_instance().check_build_queue, frequency=300, name='Builder').subscribe()

