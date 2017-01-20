#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import pprint
import random
import json

from railnation.config import (
    BASE_URL,
    LOBBY_URL,
    MELLON_CONFIG,
    XDM_CONFIG,
)
from railnation.core.common import log
from railnation.core.server import (
    session,
    server,
    ServerCall
)
from railnation.core.errors import RailNationInitializationError


msid_chars = ('1', '2', '3', '4', '5', '6', '7', '8', '9',
              'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
              'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v')


def _get_random_msid():
    random.seed()
    return ''.join([random.choice(msid_chars) for x in range(26)])


def _cut_redirect_url(data):
        try:
            s = data.index("parent.bridge.redirect({url: '")
            e = data.index("'", s+30)
        except ValueError:
            return None
        else:
            return data[s+30: e]


class AccountManager:
    """
    Representation of Rail-Nation player`s account.

    TODO:
    1. Login into lobby.
    2. Select existing world and start game in it.
    3. Join new world.
    4. Resume old login.
    """

    instance = None

    @staticmethod
    def get_instance():
        if AccountManager.instance is None:
            AccountManager.instance = AccountManager()

        return AccountManager.instance

    def __init__(self):
        self.log = log.getChild('AccountManager')
        self.log.debug('Initializing...')
        self.authenticated = False
        self.in_game = False
        self.mellon_config = {
            'url': 'https://mellon-rn.traviangames.com',
            'application': {
                'domain': 'www.rail-nation.com',
                'path': '%2Fhome%2F',
                'inGame': 0,
                'id': 'railnation',
                'countryId': 'ii',
                'instanceId': 'portal-ii',
                'languageId': 'en_GB',
                'cookieEnabled': 1,
            },
            'mellon': {
                'cookie': {
                    'domain': '.rail-nation.com'
                },
            },
        }
        self.msid = _get_random_msid()
        self.city_names = {}
        self.avatars = {}
        self.avatars_details = {}
        self.worlds = {}

        #
        # Maybe store sessions somewhere? or maybe store passwords somewhere?
        #

    def _get_mellon_url(self, action, **kwargs):
        url = self.mellon_config['url']
        if action == 'login':
            url += '/authentication/login'
        elif action == 'join':
            if 'gameWorldId' not in kwargs:
                error_msg = 'Missing parameter "gameWorldId" while construction join-world url'
                self.log.error(error_msg)
                raise RailNationInitializationError(error_msg)
            url += '/game-world/join/gameWorldId/%s' % kwargs['gameWorldId']

        # Probably order of fields is not important, but...
        url += '/applicationDomain/%(domain)s' \
               '/applicationPath/%(path)s' \
               '/applicationInGame/%(inGame)s' \
               '/applicationId/%(id)s' \
               '/applicationCountryId/%(countryId)s' \
               '/applicationInstanceId/%(instanceId)s' \
               '/applicationLanguageId/%(languageId)s' \
               '/applicationCookieEnabled/%(cookieEnabled)s' % self.mellon_config['application']

        return url

    def login(self, username, password):
        if self.authenticated:
            return

        self.log.debug('Trying to login with username: %s' % username)

        login_data = {
            'submit': 'Login',
            'email': username,
            'password': password,
        }

        auth_url = self._get_mellon_url('login')

        self.log.debug('Sending login data to server')
        response = session.post(auth_url,
                                data=login_data,
                                params={
                                    'msname': 'msid',
                                    'msid': self.msid,
                                })
        self.log.debug('Code: %s %s' % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical('Authentication failed.')
            self.log.critical('Response: %s' % response.text)
            raise RailNationInitializationError('Could not authenticate. See logs for details.')

        self.log.info('Successfully logged in to the game.')

        redirect_url = _cut_redirect_url(response.text)

        if redirect_url:
            self.log.debug('Got redirect url: %s' % redirect_url)
        else:
            self.log.error('Cannot parse redirect url from login response')
            self.log.error(response.text)
            raise RailNationInitializationError('Cannot parse redirect url from login response')

        self.authenticated = True

        try:
            self.msid = {k: v for k, v in [p.split('=') for p in redirect_url.split('&')[1].split('?')]}['msid']
        except KeyError:
            raise RailNationInitializationError('Cannot parse msid from redirect url in login response!')

        self.log.debug('Got new msid value: %s' % self.msid)
        session.cookies['msid'] = self.msid
        self.mellon_config['application']['path'] = '%2F%23%2Fmsid%3D' + self.msid

        self.log.debug('Entering Lobby...')
        response = session.get(redirect_url)
        self.log.debug('Code: %s %s' % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical('Could not enter lobby.')
            self.log.critical('Response: %s' % response.text)
            raise RailNationInitializationError('Could not enter lobby. Strange...')

        self.load_lobby_data()

    def load_lobby_data(self):
        self.log.debug('Loading lobby data')

        self.log.info('Loading city names...')
        response = session.get('http://lobby.rail-nation.com/lang/city-names.js')
        self.log.debug('Code: %s %s' % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical('Error while loading city names.')
            self.log.critical('Response: %s' % response.text)
            raise RailNationInitializationError('Error while loading city names.')

        for line in response.text.splitlines():
            if not line.strip():
                continue
            fields = line.split("'")
            try:
                names_pack_id, city_id = fields[1].split('-', 1)
                names_pack_id = int(names_pack_id)  # ensure int key
                city_name = fields[3]
            except IndexError:
                self.log.critical('Cannot parse city names: %s' % line)
                self.log.debug('fields: %s' % fields)
                self.log.critical('Response: %s' % response.text)
                raise RailNationInitializationError('Error while parsing city names.')
            else:
                try:
                    self.city_names[names_pack_id][city_id] = city_name
                except KeyError:
                    self.city_names[names_pack_id] = {city_id: city_name}
                finally:
                    self.log.debug('Pack %s: %s => %s' % (names_pack_id, city_id, city_name))

        # At this point we should have a valid cookie named "gl5SessionKey" in our session
        session_key = None
        for c in session.cookies:
            if c.name == 'gl5SessionKey':
                session_key = c.value.split('%22')[3]
                break

        self.log.debug('Found session key %s' % session_key)

        data = {
            'controller': 'player', 
            'action': 'getAll',
            'params': {},
            'session': session_key
        }
        self.log.debug('Requesting: %s' % data)

        response = session.post('http://lobby.rail-nation.com/api/index.php',
                                headers={'Content-Type': 'application/json;charset=UTF=8'},
                                data=json.dumps(data))
        self.log.debug('Code: %s %s' % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical('Error while loading lobby data.')
            self.log.critical('Response: %s' % response.text)
            raise RailNationInitializationError('Could not load lobby data. Strange...')

        r = response.json()
        if 'error' in r.keys() and r['error']:
            self.log.critical('Error while loading lobby data.')
            self.log.critical('Response: %s' % r)
            raise RailNationInitializationError('Could not load lobby data...')

        for cache_item in r['cache']:
            if cache_item['name'] == 'Collection:Avatar:':
                for avatar_cache_item in cache_item['data']['cache']:
                    avatar_id = avatar_cache_item['data']['avatarIdentifier']
                    self.log.info('Found avatar ID: %s' % avatar_id)
                    self.log.debug('Avatar data: %s' % pprint.pformat(avatar_cache_item['data']))
                    self.avatars[int(avatar_id)] = avatar_cache_item['data']
            elif cache_item['name'].startswith('AvatarInformation:'):
                avatar_id = cache_item['data']['avatarIdentifier']
                self.log.info('Found avatar info ID: %s' % avatar_id)
                self.log.debug('Avatar info: %s' % pprint.pformat(cache_item['data']))
                self.avatars_details[int(avatar_id)] = cache_item['data']

        self.log.debug('Requesting details')
        data = {
            'controller': 'cache',
            'action': 'get',
            'params': {
                'names': [
                    'Feed:%s:0' % self.mellon_config['application']['countryId'],
                    'ServerInfo:%s' % self.mellon_config['application']['countryId'],
                ]
            },
            'session': session_key,
        }

        for avatar in self.avatars.values():
            data['params']['names'].append('GameWorld:%s' % avatar['consumersId'])

        if len(self.avatars) != len(self.avatars_details):
            missing_info = set(self.avatars.keys()) - set(self.avatars_details.keys())
            for avatar_id in missing_info:
                data['params']['names'].append('AvatarInformation:%s' % avatar_id)

        self.log.debug('Requesting: %s' % data)

        response = session.post('http://lobby.rail-nation.com/api/index.php',
                                headers={'Content-Type': 'application/json;charset=UTF=8'},
                                data=json.dumps(data))
        self.log.debug('Code: %s %s' % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical('Error while loading worlds data.')
            self.log.critical('Response: %s' % response.text)
            raise RailNationInitializationError('Could not load worlds data. Strange...')

        r = response.json()
        if 'error' in r.keys() and r['error']:
            self.log.critical('Error while loading worlds data.')
            self.log.critical('Response: %s' % r)
            raise RailNationInitializationError('Could not load worlds data...')

        for cache_item in r['cache']:
            if cache_item['name'].startswith('AvatarInformation:'):
                avatar_id = cache_item['data']['avatarIdentifier']
                self.log.info('Found avatar info ID: %s' % avatar_id)
                self.log.debug('Avatar info: %s' % pprint.pformat(cache_item['data']))
                self.avatars_details[int(avatar_id)] = cache_item['data']
            elif cache_item['name'].startswith('GameWorld:'):
                world_id = cache_item['data']['consumersId']
                self.log.info('Found world ID: %s' % world_id)
                self.log.debug('World data: %s' % pprint.pformat(cache_item['data']))
                self.worlds[int(world_id)] = cache_item['data']

    def join_world(self, world_id):
        if not self.authenticated:
            raise RailNationInitializationError('Cannot join worlds without authentication')

        try:
            self.log.debug('Trying to join world: %s' % self.worlds[int(world_id)]['worldName'])
        except KeyError:
            self.log.error('Unknown world ID: %s' % world_id)
            raise RailNationInitializationError('Unknown world ID: %s' % world_id)

        world_url = self._get_mellon_url('join', gameWorldId=world_id)

        response = session.get(world_url,
                               params={
                                   'msname': 'msid',
                                   'msid': self.msid,
                               })
        self.log.debug('Code: %s %s' % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical('Join world failed.')
            self.log.critical('Response: %s' % response.text)
            raise RailNationInitializationError('Join world failed. See logs for details.')

        redirect_url = _cut_redirect_url(response.text)

        if redirect_url:
            self.log.debug('Got redirect url: %s' % redirect_url)
        else:
            self.log.error('Cannot parse redirect url from world-join response')
            self.log.error(response.text)
            raise RailNationInitializationError('Cannot parse redirect url from world-join response')

        self.log.info('Successful world join.')

        try:
            self.msid = {k: v for k, v in [p.split('=') for p in redirect_url.split('&')[1].split('?')]}['msid']
        except KeyError:
            raise RailNationInitializationError('Cannot parse msid from redirect url in world-join response!')

        self.log.debug('Got new msid value: %s' % self.msid)
        session.cookies['msid'] = self.msid

        self.log.info('Entering world: %s' % self.worlds[int(world_id)]['worldName'])
        response = session.get(redirect_url)
        self.log.debug('Code: %s %s' % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical('Could not enter world.')
            self.log.critical('Response: %s' % response.text)
            raise RailNationInitializationError('Could not enter world. Strange...')

        global server
        server = ServerCall(self.worlds[int(world_id)]['baseUrl'])

        self.in_game = True


