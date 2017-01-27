#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import datetime
import random

import cherrypy
from cherrypy.process.plugins import Monitor

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.const import building_names
from railnation.managers.avatar import AvatarManager
from railnation.managers.station import StationManager
from railnation.managers.resources import ResourcesManager
from railnation.managers.ticket import TicketManager


class CollectManager:
    """
    Manages bonuses collection from restaurant, mall and hotel.
    Both yours and your association.
    With option to automatically open any free tickets, you got.
    """
    instance = None

    @staticmethod
    def get_instance():
        if CollectManager.instance is None:
            CollectManager.instance = CollectManager()
        return CollectManager.instance

    def __init__(self):
        self.log = log.getChild('CollectManager')
        self.log.debug('Initializing...')
        self.auto_collect = False
        self.auto_open_tickets = False
        self.schedule = {}
        self.stats = {}

    def check(self):
        if not self.auto_collect:
            return

        avatar = AvatarManager.get_instance()
        player_id = avatar.id

        if player_id not in self.schedule.keys():
            self._create_schedule(player_id)

        for building_id in (7, 8, 9):
            ready_at = self.schedule[player_id + '-' + str(building_id)]
            if datetime.datetime.now > ready_at:
                r = self.collect(player_id, building_id)
                if r:
                    self._create_schedule(player_id)

    def _create_schedule(self, player_id):
        station = StationManager.get_instance(player_id)
        for building_id in (7, 8, 9):
            # add random delay to production time
            self.schedule[player_id + '-' + str(building_id)] = station.buildings[building_id]['production_at'] + datetime.timedelta(seconds=random.randint(1, 10))

    def collect(self, player_id, building_id):
        if building_id in (8, 9):
            self.log.debug('Check if player %s have reached money limit' % player_id)
            r = server.call('ResourceInterface', 'isLimitReached', [player_id])
            self.log.debug('Result: %s' % r)
            if r:
                if self.auto_collect:
                    self.log.debug('Reschedule collecting after 1 hour')
                    self.schedule[player_id + '-8'] = datetime.datetime.now() + datetime.timedelta(seconds=3600)
                    self.schedule[player_id + '-9'] = datetime.datetime.now() + datetime.timedelta(seconds=3600)
                return False

        resources = ResourcesManager.get_instance()
        self.log.debug('Collecting %s from %s' % (building_names[int(building_id)], player_id))
        tickets_before = resources.free_tickets_count
        r = server.call('BuildingInterface', 'collect', [int(building_id), player_id])
        station = StationManager.get_instance(player_id)
        station.update_building(r)
        if tickets_before < resources.free_tickets_count:
            self.log.info('Got free ticket')
        return True

    # # interface=BuildingInterface&method=getIFrame
    # # {"checksum":"e0cf78b7306751b66e07c2c43d5a9cc3","client":1,"parameters":[],"hash":"d751713988987e9331980363e24189ce"}
    # #
    # # interface=BuildingInterface&method=videoWatched
    # # {"checksum":"e0cf78b7306751b66e07c2c43d5a9cc3","client":1,"parameters":["d380ae55-938c-ad81-688b-46d471f534d7",8,"1483873839504d380ae55938cad81688b46d471f534d7","95cfdc536f9e86fd65a1afab3f8055e6"],"hash":"1c0835c13adfb2a7c74cf9c86c319e6c"}
    # #
    # #  http://media.oadts.com/www/delivery/xs.php?vrid=1483873839504d380ae55938cad81688b46d471f534d7-1483873678-0b0ecc3975c89c249ad021dc656db515&vaid=7e238e62e7a6a05048534a0cfea7c509&csid=17129-3590
    # #  <?xml version="1.0"?><XSIGN><key>1483873839504d380ae55938cad81688b46d471f534d7</key><sign>95cfdc536f9e86fd65a1afab3f8055e6</sign></XSIGN>
    # def watch_video(self, player_id, building_id):
    #     pass
    #
    # def watch_second_video(self, player_id, building_id):
    #     pass

Monitor(cherrypy.engine, CollectManager.get_instance().check, frequency=10).subscribe()
