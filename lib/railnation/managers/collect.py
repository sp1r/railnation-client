#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import random
import datetime
import time
import cherrypy
from cherrypy.process.plugins import Monitor

from railnation.core.common import log
from railnation.core.server import server
from railnation.managers.avatar import AvatarManager
from railnation.managers.association import AssociationManager
from railnation.managers.station import StationManager
from railnation.managers.resources import ResourcesManager
from railnation.managers.properties import PropertiesManager
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
        """
        :rtype: CollectManager
        """
        if CollectManager.instance is None:
            CollectManager.instance = CollectManager()
        return CollectManager.instance

    def __init__(self):
        self.log = log.getChild('CollectManager')
        self.log.debug('Initializing...')
        self.auto_collect = False
        self.auto_open_tickets = False
        self.auto_watch = False
        self.schedule = {}
        self.next_collection = None
        self.stats = {
            'collected': 0,
            'errors': 0,
            'tickets': 0
        }
        self.history = []
        self.collect_delay = (3, 30)

    def collect_player(self, player_id=None):
        """
        In-game procedure to collect bonuses is to open player`s station and collect everything
        available. This method mimics this behaviour.

        :param player_id: player`s uuid
        :return: True if something is collected, False otherwise
        """
        if player_id is None:
            player_id = AvatarManager.get_instance().id

        result = False

        self.log.debug('Loading player station data: %s' % player_id)
        buildings = StationManager.get_instance().get_buildings(player_id)

        self.log.debug('Check if player %s have reached money limit' % player_id)
        r = server.call('ResourceInterface', 'isLimitReached', [player_id])
        self.log.debug('Money limit reached: %s' % r)

        if buildings[7]['production_at'] <= datetime.datetime.now():
            self.log.debug('Hotel ready')
            self.collect(7, player_id)
            buildings[7]['production_at'] = datetime.datetime.now() + datetime.timedelta(seconds=10800)
            result = True

        if buildings[8]['production_at'] <= datetime.datetime.now():
            self.log.debug('Restaurant ready')
            if r:
                self.log.debug('Skip collecting cash bonuses')
                buildings[8]['production_at'] = datetime.datetime.now() + datetime.timedelta(seconds=3600)
            else:
                self.collect(8, player_id)
                buildings[8]['production_at'] = datetime.datetime.now() + datetime.timedelta(seconds=5400)
            result = True

        if buildings[9]['production_at'] <= datetime.datetime.now():
            self.log.debug('Mall ready')
            if r:
                self.log.debug('Skip collecting cash bonuses')
                buildings[9]['production_at'] = datetime.datetime.now() + datetime.timedelta(seconds=3600)
            else:
                self.collect(9, player_id)
                buildings[9]['production_at'] = datetime.datetime.now() + datetime.timedelta(seconds=21600)
            result = True

        next_production = min(
            [buildings[i]['production_at'] for i in (7, 8, 9)]
        )
        try:
            self.schedule[int(time.mktime(next_production.timetuple()))].append(player_id)
        except KeyError:
            self.schedule[int(time.mktime(next_production.timetuple()))] = [player_id]

        return result

    def collect(self, building_id, player_id=None):
        if player_id is None:
            player_id = AvatarManager.get_instance().id

        building_id = int(building_id)
        assert building_id in (7, 8, 9)
        building_name = PropertiesManager.get_instance().buildings[building_id]['name']

        resources = ResourcesManager.get_instance()
        self.log.debug('Collecting from %s (owner: %s)' % (building_name, player_id))
        tickets_before = resources.free_tickets_count
        r = server.call('BuildingInterface', 'collect', [int(building_id), player_id])

        if 'productionTimeLeft' in r:
            self.stats['collected'] += 1
            self.log.debug('Bonus collected (%s total)' % self.stats['collected'])
        else:
            self.stats['errors'] += 1
            self.log.debug('Collecting error (%s total)' % self.stats['errors'])
            return False

        if tickets_before < resources.free_tickets_count:
            self.stats['tickets'] += 1
            self.log.info('Got free ticket (%s total)' % self.stats['tickets'])
            return True
        else:
            return True

    def check(self):
        if not self.auto_collect:
            return

        if not self.schedule:
            self._init_schedule()

        closest_production = min(self.schedule.keys())
        while closest_production <= time.time():
            for player in self.schedule.pop(closest_production):
                self.log.debug('Auto-collecting player: %s' % player)
                self.collect_player(player)
            closest_production = min(self.schedule.keys())
            self.next_collection = min(self.schedule.keys()) + random.randint(*self.collect_delay)
            self.log.debug('Next collecting at: %s' % datetime.datetime.fromtimestamp(self.next_collection))

    def _init_schedule(self):
        association = AssociationManager.get_instance().get_association()
        if association is not None:
            collect_targets = association['members']
        else:
            collect_targets = [AvatarManager.get_instance().id]

        for player in collect_targets:
            station = StationManager.get_instance().get_buildings(player)
            next_production = min(
                [station[i]['production_at'] for i in (7, 8, 9)]
            )
            try:
                self.schedule[int(time.mktime(next_production.timetuple()))].append(player)
            except KeyError:
                self.schedule[int(time.mktime(next_production.timetuple()))] = [player]

        self.next_collection = min(self.schedule.keys()) + random.randint(*self.collect_delay)
        self.log.debug('Next collection at: %s' % datetime.datetime.fromtimestamp(self.next_collection))

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

Monitor(cherrypy.engine, CollectManager.get_instance().check, frequency=10, name='Auto-Collecting').subscribe()
