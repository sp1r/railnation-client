#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import math
import hashlib
import random
import datetime
import time
import json
import cherrypy
from cherrypy.process.plugins import Monitor
try:
    from xml.etree import cElementTree as ElementTree
except ImportError, e:
    from xml.etree import ElementTree

from railnation.core.common import log
from railnation.core.server import (
    session,
    server
)
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

        player_name = AvatarManager.get_instance().get_name(player_id)

        building_id = int(building_id)
        assert building_id in (7, 8, 9)
        building_name = PropertiesManager.get_instance().buildings[building_id]['name']

        resources = ResourcesManager.get_instance()
        self.log.debug('Collecting from %s (owner: %s)' % (building_name, player_name))
        tickets_before = resources.free_tickets_count
        r = server.call('BuildingInterface', 'collect', [building_id, player_id])

        result = {
            "date": int(time.time()),
            "player_id": player_id,
            "player_name": player_name,
            "building_id": building_id,
            "building_name": building_name,
            "result": False,
            "ticket": False
        }

        if 'productionTimeLeft' in r:
            self.stats['collected'] += 1
            self.log.debug('Bonus collected (%s total)' % self.stats['collected'])
        else:
            self.stats['errors'] += 1
            self.log.debug('Collecting error (%s total)' % self.stats['errors'])
            return False

        result['result'] = True

        if tickets_before < resources.free_tickets_count:
            self.stats['tickets'] += 1
            self.log.info('Got free ticket (%s total)' % self.stats['tickets'])
            result['ticket'] = True

        if self.auto_collect:
            self.history.append(result)

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
                time.sleep(1)  # don`t ddos game server
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

    def watch_video(self, player_id, building_id):
        building_id = int(building_id)
        assert building_id in (7, 8, 9)

        buildings = StationManager.get_instance().get_buildings(player_id)
        if buildings[building_id]['video_watched']:
            self.log.error('Video already watched')
            return

        building_name = PropertiesManager.get_instance().buildings[building_id]['name']
        player_name = AvatarManager.get_instance().get_name(player_id)
        self.log.debug('Watching video on %s of %s...' % (building_name, player_name))
        key, sign = self._watch_video()

        if key is None or sign is None:
            self.log.error('Got junk instead of key and sign, watching failed.')
            return None

        r = server.call('BuildingInterface', 'videoWatched', [
            player_id,
            building_id,
            key, sign
        ])

        if not r:
            self.log.debug('Video watched')
            return None

        self.log.debug('Can watch second video! Hooray!')
        key, sign = self._watch_video()

        if key is None or sign is None:
            self.log.error('Got junk instead of key and sign, watching failed.')
            return None

        r = server.call('BuildingInterface', 'secondWatch', [key, sign])
        self.log.info('Got reward for video watching: %s' % r)

        return r
        #
        # interface=LotteryInterface&method=buyLotteryTicketCheap [] true/false
        #
        # interface=LotteryInterface&method=exchangeCoins [3] (science points)

    def _watch_video(self):
        self.log.debug('Watching Ads video...')

        r = server.call('BuildingInterface', 'getIFrame', [])
        if not r.startswith('http'):
            self.log.error('Get Iframe url failed. Got: %s' % r)
            return False

        self.log.debug('Got base iframe url: %s' % r)

        params = {k: v for k,v in [x.split('=') for x in r.split('?')[1].split('&')]}
        self.log.debug('Parsed params: %s' % params)
        try:
            zoneid = params['zoneid']
        except KeyError:
            self.log.error('No zone ID in response. Cannot continue')
            return False

        self.log.debug('Got zone ID: %s' % zoneid)

        vrid = str(int(time.time() * 1000)) + AvatarManager.get_instance().id.replace('-', '')
        self.log.debug('Generated vrid: %s' % vrid)
        cb = int(random.random() * 500)
        self.log.debug('Generated cb: %s' % cb)

        r = session.get(r, params={
            'vrid': vrid,
            'cb': cb,
            'loc': server.server_url
        })
        self.log.debug('Code: %s %s' % (r.status_code,
                                        r.reason))

        if r.status_code != 200:
            self.log.error('Could not get adv video iFrame.')
            self.log.error('Response: %s' % r.text)
            return False

        # Mighty parsing
        self.log.debug('Raw iframe: %s' % r.text)
        vast_urls = None
        log_urls = None
        for line in r.text.splitlines():
            line = line.strip()
            if line.startswith('vastUrls'):
                self.log.debug('Parsing line: %s' % line)
                vast_urls_string = line.split(':', 1)[1][:-1]
                self.log.debug('Got vastUrls string: %s' % vast_urls_string)
                try:
                    vast_urls = json.loads(vast_urls_string)
                except ValueError:
                    self.log.error('Cannot parse vastUrls: %s' % vast_urls_string)
                    return False
            elif line.startswith('logUrls'):
                self.log.debug('Parsing line: %s' % line)
                log_urls_string = line.split(':', 1)[1][:-1]
                self.log.debug('Got logUrls string: %s' % log_urls_string)
                try:
                    log_urls = json.loads(log_urls_string.replace("'+'", '').replace("'", '"'))
                except ValueError:
                    self.log.error('Cannot parse logUrls: %s' % log_urls_string)
                    return False

            elif 'xsign' in line:
                self.log.debug('Parsing line: %s' % line)
                vrid = ''
                xsign_parts = line.split("'")
                for index, xpart in enumerate(xsign_parts):
                    if 'vrid' in xpart:
                        vrid = xsign_parts[index + 1]
                self.log.debug('Got vrid: %s' % vrid)

        if vast_urls is None or log_urls is None:
            self.log.error('Parsing of Iframe failed. Cannot watch video.')
            return False

        for vast in vast_urls:
            self.log.debug('Sending shift event to oadts')
            r = session.get('http://media.oadts.com/www/delivery/fc.php', params={
                'script': 'deliveryLog:oaLogEvent:logEvent',
                'zoneid': zoneid,
                'bannerid': vast['bid'],
                'eventId': 21,
                'cb': int(math.floor(random.random() * 99999999999)),
                'loc': server.server_url
            })
            self.log.debug('Code: %s %s' % (r.status_code,
                                            r.reason))

            if r.status_code != 200:
                self.log.error('Some shit happened, but we will try to continue')
                self.log.error('Response: %s' % r.text)

            if 'media.oadts' not in vast['url']:
                self.log.debug('Skipping url: %s' % vast['url'])
                continue

            self.log.debug('Requesting vast')
            r = session.get(vast['url'])
            self.log.debug('Code: %s %s' % (r.status_code,
                                            r.reason))

            if r.status_code != 200:
                self.log.error('Some shit happened, but we will try to continue')
                self.log.error('Response: %s' % r.text)
                continue

            self.log.debug('Parsing XML: %s' % r.text)
            tree = ElementTree.fromstring(r.text)
            video_duration = tree.find('Ad').find('InLine').find('Creatives').find('Creative').find('Linear').find('Duration').text
            self.log.debug('Video duration: %s' % video_duration)
            hours, minutes, seconds = video_duration.split(':')
            total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            self.log.debug('Total seconds: %s' % total_seconds)

            log_url = log_urls[vast['bid']]
            self.log.debug('Notifying media.oadts.com that we`ve choosed this one: %s' % log_url)
            r = session.get(log_url, params={'plr': 1})
            self.log.debug('Code: %s %s' % (r.status_code,
                                            r.reason))

            if r.status_code != 200:
                self.log.error('Some shit happened, but we will try to continue')
                self.log.error('Response: %s' % r.text)

            watch_event_base_url = 'http://media.oadts.com/www/delivery/fc.php?' \
                                   'script=deliveryLog:oxLogVast:logImpressionVast&' \
                                   'banner_id=' + vast['bid'] + '&' \
                                   'zone_id=' + zoneid + '&' \
                                   'cb=' + str(random.random()) + '&vast_event='
            self.log.debug('Base url for watch video events: %s' % watch_event_base_url)
            self._simulate_watching(total_seconds, watch_event_base_url)

            self.log.debug('Send finish event to oadts')
            r = session.get('http://media.oadts.com/www/delivery/fc.php', params={
                'script': 'deliveryLog:oaLogEvent:logEvent',
                'zoneid': zoneid,
                'bannerid': 0,
                'eventId': 23,
                'cb': int(math.floor(random.random() * 99999999999)),
                'loc': server.server_url
            })
            self.log.debug('Code: %s %s' % (r.status_code,
                                            r.reason))

            if r.status_code != 200:
                self.log.error('Some shit happened, but we will try to continue')
                self.log.error('Response: %s' % r.text)

            self.log.debug('Request sign for watched video.')
            params = {
                'vrid': vrid,
                'vaid': self._get_magic_hash(vrid, zoneid, vast['bid']),
                'csid': '-'.join((vast['bid'], zoneid)),
            }
            self.log.debug('Request params: %s' % params)
            r = session.get('http://media.oadts.com/www/delivery/xs.php', params=params)
            self.log.debug('Code: %s %s' % (r.status_code,
                                            r.reason))

            if r.status_code != 200:
                self.log.error('Some shit happened, possible we`ll got dick instead of a reward')
                self.log.error('Response: %s' % r.text)

            self.log.debug('Parsing XML: %s' % r.text)
            tree = ElementTree.fromstring(r.text)
            key = tree.find('key').text
            self.log.debug('Got key: %s' % key)
            sign = tree.find('sign').text
            self.log.debug('Got sign: %s' % sign)

            return key, sign

    def _get_magic_hash(self, vrid, zoneid, bannerid):
        classname = 'org.ova.vast.config.groupings::XSignConfigGroup'
        count = 1
        c2 = ''
        for index, character in enumerate(classname):
            if character in ('.', ':'):
                c2 += str(count^index)
                count += 1
            else:
                c2 += character
        garbage = vrid + 'Y' + zoneid + 'p' + bannerid
        return hashlib.md5(c2 + garbage[::-1]).hexdigest()

    def _simulate_watching(self, duration, event_url_base):
        quarter = duration / 4 + 1

        r = session.get(event_url_base + 'start')
        self.log.debug('Code: %s %s' % (r.status_code,
                                        r.reason))

        if r.status_code != 200:
            self.log.error('Some shit happened, but we will try to continue')
            self.log.error('Response: %s' % r.text)

        for position in ('firstQuartile', 'midpoint', 'thirdQuartile', 'complete'):
            self.log.debug('Watching (Sleeping) for %s seconds...' % quarter)
            time.sleep(quarter)
            self.log.debug('Reached: %s' % position)
            r = session.get(event_url_base + position)
            self.log.debug('Code: %s %s' % (r.status_code,
                                            r.reason))

            if r.status_code != 200:
                self.log.error('Some shit happened, but we will try to continue')
                self.log.error('Response: %s' % r.text)

    # # interface=BuildingInterface&method=videoWatched
    # # {"checksum":"e0cf78b7306751b66e07c2c43d5a9cc3","client":1,"parameters":["d380ae55-938c-ad81-688b-46d471f534d7",8,"1483873839504d380ae55938cad81688b46d471f534d7","95cfdc536f9e86fd65a1afab3f8055e6"],"hash":"1c0835c13adfb2a7c74cf9c86c319e6c"}


Monitor(cherrypy.engine, CollectManager.get_instance().check, frequency=10, name='Auto-Collecting').subscribe()
