# -*- coding:utf-8 -*-
"""
Entities to be used over the whole application

This includes:
    client
    client_info
    self_id
    game_properties
    game_language
    game_info
    main_menu

This module can be used to track game loading process. It`s all here.
"""

import sys
import os
import time

from railnation.core.railnation_errors import (
    NotAuthenticated,
)

from railnation.core.railnation_log import log
log.debug('Loading module: Globals')


# web client
from railnation.core.railnation_client import Client
client = Client()
log.debug('Web Client created.')

from railnation.core.railnation_authentication import authenticate
authenticate(client)


# load parameters from server
client.session.headers.update({'content-type': 'application/json'})

self_id = str(client.produce('AccountInterface',
                             'is_logged_in',
                             [client.webkey])['Body'])
if self_id == 'False':
    log.critical('Got "False" instead of player ID while loading!')
    raise NotAuthenticated('Cannot get your id.')

log.debug('Web Client authenticated.')

r = client.produce('PropertiesInterface',
                   'getData',
                   [])['Body']

properties = r['properties']
properties['client'] = r['client']

client_info = client.produce('KontagentInterface',
                             'getData',
                             [])['Body']

language = str(client.produce('AccountInterface',
                              'getLanguage',
                              [])['Body'])

# client.session.headers.update({'content-type': ''})
# TODO: расследовать, одинаковый ли id у ассетов на разных серверах
# r = client.session.get('http://s3.railnation.ru/web/assets/ea24d4af2c56'
#                        '6004782f750f940615e5/languagedata.ru-RU.zip',
#                        stream=True)
#
# tf = tempfile.TemporaryFile()
# tf.write(zlib.decompress(r.raw.read()))
# tf.seek(0)
# # #parse this file
# tf.close()
# print('.', end='')
#
# r = client.session.get('http://s3.railnation.ru/web/assets/ea24d4af2c56'
#                        '6004782f750f940615e5/languagedata.city-Names.zip',
#                        stream=True)
#
# tf = tempfile.TemporaryFile()
# tf.write(zlib.decompress(r.raw.read()))
# tf.seek(0)
# # #parse this file too
# tf.close()
# print('.', end='')
# client.session.headers.update({'content-type': 'application/json'})


# main menu
class MainMenu:
    def __init__(self):
        self.menu = {}
        self.names = {}

    def add_entry(self, handler):
        if handler.key in self.menu:
            raise RuntimeError('Menu Error: Key "%s" is already in use '
                               'by handler: %s' %
                               (handler.key, self.names[handler.key]))
        self.menu[handler.key] = handler.menu
        self.names[handler.key] = handler.name

    def items(self):
        return self.menu.items()

    def __iter__(self):
        return self.menu.__iter__()

    def __getitem__(self, item):
        return self.names.__getitem__(item)

menu = MainMenu()
log.debug('Main menu instantiated.')


# basic game info container
class InfoContainer:
    def __init__(self):
        self.corp_name = ''
        self.rank = 0
        self.next_refresh = 0.0
        self.refresh_period = 120.0
        self.resources = {}
        self.stars = 0

        r = client.produce('AccountInterface',
                           'get',
                           [self_id])['Body']
        self.name = r['name']
        r = client.produce('ProfileInterface',
                           'getVCard',
                           [[self_id]])['Body']
        self.stars = r[self_id]['stars']

    def store(self, resource, amount):
        self.resources[resource] += amount
        self._update_infos()

    def take(self, resource, amount):
        if self.resources[resource] >= amount:
            self.resources[resource] -= amount
            self._update_infos()
            return True
        else:
            return False

    def refresh(self):
        self.next_refresh = time.time() + self.refresh_period
        r = client.produce('GUIInterface',
                           'get_gui',
                           [])['Body']
        try:
            self.corp_name = r['corporation']['name']
        except KeyError:
            self.corp_name = ''
        for res_id, data in r['resources'].items():
            self.resources[int(res_id)] = int(data['amount'])
        self._update_infos()

    def get_infos(self):
        if time.time() > self.next_refresh:
            self.refresh()
        return self.infos

    def _update_infos(self):
        self.infos = (
            'Name    : %s' % self.name,
            'Copr    : %s' % self.corp_name,
            'Prestige: %s' % self.resources[3],
            'Rank    : %s' % self.rank,
            'Money   : %s' % self.resources[1],
            'Gold    : %s' % self.resources[2],
        )

game_info = InfoContainer()


# main screen
from railnation.core.railnation_screen import Screen
screen = Screen(menu, game_info)
log.debug('Screen ready.')


################################################################################
# python 3?
is_py3 = sys.version_info >= (3, 3)

# linux?
is_linux = sys.platform.startswith('linux')

# set path
work_path = os.path.realpath(os.path.dirname(__file__))
handlers_path = os.path.realpath(os.path.join(work_path, '..', 'handlers'))

# temporary add pages dir to sys.path, we will restore original value
# after all pages are imported
orig_sys_path = sys.path[:]
sys.path.append(handlers_path)