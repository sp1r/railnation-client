#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import random
import json
import time
import zipfile
import StringIO
try:
    from xml.etree import cElementTree as ElementTree
except ImportError, e:
    from xml.etree import ElementTree

from railnation.core.common import log
from railnation.core.server import server
from railnation.core.errors import RailNationInitializationError


class PropertiesManager:
    """
    Game properties.

    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: PropertiesManager
        """
        if PropertiesManager.instance is None:
            PropertiesManager.instance = PropertiesManager()

        return PropertiesManager.instance

    def __init__(self):
        self.log = log.getChild('PropertiesManager')
        self.log.debug('Initializing...')

        self.buildings = {}

        self.l18n = {}

        data = server.call('ServerInfoInterface', 'getInfo', [])

        self.config_path = data['config']
        self.log.debug('Config path: %s' % self.config_path)
        self.game_speed = data['gameSpeed'] if 'gameSpeed' in data.keys() else 1
        self.log.debug('Game speed: %s' % self.game_speed)
        self.map_file = data['map']
        self.log.debug('Map file: %s' % self.map_file)
        self.town_name_offset = data['townNameOffset']
        self.log.debug('Town names offset: %s' % self.town_name_offset)
        self.town_name_pack = data['townNamePackage']
        self.log.debug('Town names package: %s' % self.town_name_pack)
        self.version = data['version']
        self.log.debug('Game version: %s' % self.version)
        self.world_name = data['worldName']
        self.log.debug('World name: %s' % self.world_name)
        self.available_lang = data['availableLanguages']
        self.log.debug('Available languages: %s' % self.available_lang)

    def load_station_buildings(self):
        for i, b in enumerate((
            'engine_house',
            'station',
            'maintenance_hall',
            'construction_yard',
            'bank',
            'licence',
            'labor',
            'hotel',
            'restaurant',
            'mall',
        )):
            url = '/properties/%s/building_%s.json?%s' % (
                self.config_path, b, random.random()
            )
            self.log.debug('Loading: %s' % url)
            r = server.get(url)
            self.log.debug('Raw data: %s' % r)
            self.buildings[i] = json.loads(r)

    def get_tech_tree(self):
        url = '/properties/%s/techtree.json?%s' % (
            self.config_path, random.random()
        )
        self.log.debug('Loading: %s' % url)
        r = server.get(url)
        self.log.debug('Raw data: %s' % r)
        return json.loads(r)

    def get_trains(self):
        url = '/properties/%s/trains.json?%s' % (
            self.config_path, random.random()
        )
        self.log.debug('Loading: %s' % url)
        r = server.get(url)
        self.log.debug('Raw data: %s' % r)
        return json.loads(r)

    def get_train_upgrades(self):
        url = '/properties/%s/train_upgrades.json?%s' % (
            self.config_path, random.random()
        )
        self.log.debug('Loading: %s' % url)
        r = server.get(url)
        self.log.debug('Raw data: %s' % r)
        return json.loads(r)

    def load_language_data(self):
        # http://s1.rail-nation.com/lang/languagedata.en-GB.zip?nocache=1484725322788
        url = '/lang/languagedata.%s.zip?nocache=%s' % (
            self.available_lang[0],
            int(time.time() * 1000)
        )
        self.log.debug('Loading: %s' % url)
        z = server.get(url, raw=True)
        r = zipfile.ZipFile(StringIO.StringIO(z)).read('languagedata.%s.xml' % self.available_lang[0])
        self.log.debug('Raw data: %s' % r)
        self.log.debug('Parsing XML')
        tree = ElementTree.fromstring(r)
        for tu in tree.find('body').findall('tu'):
            tuid = tu.attrib['tuid']
            tuv = tu.find('tuv').find('seg').text
            self.log.debug('%s = %s' % (tuid, tuv))
            self.l18n[tuid] = tuv

    def get_tech_name(self, tech_id):
        try:
            return self.l18n['IDS_TECH_NAME_' + tech_id]
        except KeyError:
            self.log.warning('Cannot find tech name for id: %s' % tech_id)
            return ''

