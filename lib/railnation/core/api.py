#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import cherrypy
from cherrypy import _cperror
import json
import time
import datetime

from railnation.core.common import (
    log,
    IS_PY3
)
from railnation.core.errors import (
    RailNationClientError,
    RailNationDoubleLogin,
    RailNationNotAuthenticated,
)
from railnation.core.server import (
    server,
    recreate_session
)
from railnation.managers.account import AccountManager
from railnation.managers.avatar import AvatarManager
from railnation.managers.association import AssociationManager
from railnation.managers.collect import CollectManager
from railnation.managers.resources import ResourcesManager
from railnation.managers.station import StationManager


def process_error_500():
    ex_type, ex_value, ex_traceback = _cperror._exc_info()
    log.error('Exception path: %s' % ex_type)

    if ex_type is RailNationDoubleLogin:
        log.error('Double login detected. Invalidating this session.')
        cherrypy.response.status = 200
        cherrypy.response.body = json.dumps({
            'code': 3,
            'message': 'Double login. Session invalidated.',
            'data': None
        })
        recreate_session()
        server.destroy()
        AccountManager.get_instance().authenticated = False
        AccountManager.get_instance().in_game = False

    elif ex_type is RailNationNotAuthenticated:
        log.error('Session is not authenticated')
        cherrypy.response.status = 200
        cherrypy.response.body = json.dumps({
            'code': 2,
            'message': 'Not authenticated to process request.',
            'data': None
        })

    elif ex_type is RailNationClientError:
        log.error('Errors in client logic. Panicking.')
        cherrypy.response.status = 500
        cherrypy.response.body = json.dumps({
            'code': 1,
            'message': 'Internal error',
            'data': None
        })

    else:
        cherrypy.response.status = 500
        cherrypy.response.body = json.dumps({
            'code': 500,
            'message': 'Internal error',
            'data': None
        })


class RailNationClientAPIv1:

    _cp_config = {'request.error_response': process_error_500}

    def __init__(self):
        self.log = log.getChild('APIv1')

    ####################################################################################################################
    #
    # Pre-game methods
    #
    ####################################################################################################################

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def login(self):
        self.log.debug('%s /login called' % cherrypy.request.method)
        if cherrypy.request.method == 'OPTIONS':
            return ''

        elif cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        content_length = cherrypy.request.headers['Content-Length']
        self.log.debug('Body length: %s' % content_length)

        raw_body = cherrypy.request.body.read(int(content_length))
        self.log.debug('Raw body: %s' % raw_body)

        if IS_PY3:
            raw_body = str(raw_body)[2:-1]
        else:
            raw_body = str(raw_body)

        try:
            request = json.loads(str(raw_body))
        except ValueError as err:
            error_msg = 'Request body is not a json object.'
            self.log.error(error_msg)
            self.log.error(err)
            return {'code': 1, 'message': error_msg, 'data': None}

        try:
            username = request['username']
            password = request['password']
        except KeyError:
            error_msg = 'Request body is missing keys: "username" or "password"'
            self.log.error(error_msg)
            return {'code': 1, 'message': error_msg, 'data': None}

        self.log.debug('Continue as: %s' % username)
        manager = AccountManager.get_instance()

        if manager.authenticated:
            self.log.warning('Game session already authenticated')
            return {'code': 0, 'message': 'Already authenticated', 'data': True}

        try:
            manager.login(username, password)
        except RailNationClientError:
            self.log.error('Login Errors')

        if manager.authenticated:
            self.log.debug('Auth success')
            return {'code': 0, 'message': 'Auth success', 'data': True}
        else:
            self.log.debug('Auth failed')
            return {'code': 1, 'message': 'Auth failed', 'data': False}

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def worlds(self):
        self.log.debug('%s /worlds called' % cherrypy.request.method)

        if cherrypy.request.method != 'GET':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        manager = AccountManager.get_instance()

        if not manager.authenticated:
            self.log.error('Cannot list worlds without authentication')
            return {'code': 1, 'message': 'Not authenticated', 'data': None}

        response = []

        self.log.debug('Listing %s avatars' % len(manager.avatars))
        for avatar_id, avatar_data in manager.avatars.items():
            self.log.debug('Processing avatar: %s' % avatar_id)

            try:
                avatar_info = manager.avatars_details[int(avatar_id)]
            except KeyError:
                self.log.critical('Avatar details not found. Error in initialization!')
                return {'code': 2, 'message': 'Initialization error', 'data': None}
            self.log.debug('Avatar info ID: %s' % avatar_info['avatarIdentifier'])

            try:
                world_info = manager.worlds[int(avatar_data['consumersId'])]
            except KeyError:
                self.log.critical('World data not found. Error in initialization!')
                return {'code': 2, 'message': 'Initialization error', 'data': None}
            self.log.debug('Avatar world name: %s' % world_info['worldName'])

            try:
                city_name = manager.city_names[int(world_info['cityNamesPackage'])][avatar_info['cityId']]
            except KeyError:
                self.log.warning('Cannot load city name for ID: %s' % avatar_info['cityId'])
                city_name = ''
            
            try:
                response.append({
                    'avatarName': avatar_data['avatarName'],
                    'avatarId': avatar_data['avatarIdentifier'],
                    'country': avatar_data['country'],
                    'isBanned': avatar_data['isBanned'],
                    'isSuspended': avatar_data['isSuspended'],
                    'playerPrestige': avatar_info['playerPrestige'],
                    'playerRank': avatar_info['playerRank'],
                    'cityName': city_name,
                    'cityLevel': avatar_info['cityLevel'],
                    'associationName': avatar_info['associationName'],
                    'associationPrestige': avatar_info['associationPrestige'],
                    'associationRank': avatar_info['associationRank'],
                    'lastLogin': avatar_info['lastLogin'],
                    'era': world_info['era'],
                    'eraDay': world_info['eraDay'],
                    'eraTimeLapsed': world_info['eraTimeLapsed'],
                    'eraTimeLeft': world_info['eraTimeLeft'],
                    'playersOnline': world_info['playersOnline'],
                    'playersActive': world_info['playersActive'],
                    'playersRegistered': world_info['playersRegistered'],
                    'scenario': world_info['scenario'],
                    'worldName': world_info['worldName'],
                    'worldId': world_info['consumersId']
                })
            except KeyError as err:
                self.log.error('Something wrong in lobby data')
                self.log.error(err)
                return {'code': 1, 'message': 'Lobby data error', 'data': None}

        self.log.debug('Returning %s worlds' % len(response))
        return {'code': 0, 'message': 'OK', 'data': response}

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def join(self, world_id):
        self.log.debug('%s /join/%s called' % (cherrypy.request.method, world_id))
        manager = AccountManager.get_instance()

        try:
            manager.join_world(world_id)
        except RailNationClientError as err:
            self.log.critical('Cannot load game')
            self.log.critical(err)
            return {'code': 1, 'message': str(err), 'data': False}
        else:

            if manager.in_game:
                return {'code': 0, 'message': 'Game started', 'data': True}
            else:
                return {'code': 1, 'message': 'Game not started', 'data': False}

    ####################################################################################################################
    #
    # Interface methods
    #
    ####################################################################################################################

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def resources(self):
        self.log.debug('%s /resources called' % cherrypy.request.method)

        if cherrypy.request.method != 'GET':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        manager = ResourcesManager.get_instance()

        if len(manager.resources.keys()) == 0:
            return {
                'code': 1,
                'message': 'Resources not initialized',
                'data': {
                    'amount': {},
                    'limit': {},
                }
            }

        else:
            return {
                'code': 0,
                'message': 'OK',
                'data': {
                    'amount': manager.resources,
                    'limit': manager.resources,
                }
            }

    ####################################################################################################################
    #
    # Association methods
    #
    ####################################################################################################################

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def association(self, association_id=None):
        self.log.debug('%s /association/%s called' % (cherrypy.request.method, association_id))

        if cherrypy.request.method != 'GET':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        if association_id is None:
            association_id = AvatarManager.get_instance().association_id
            self.log.debug('Using active player association id: %s' % association_id)

        try:
            association = AssociationManager.get_instance().get_association(association_id)

        except RailNationClientError as err:
            self.log.error('Cannot get association info: %s' % association_id)
            self.log.error(str(err))
            return {
                'code': 1,
                'message': str(err),
                'data': None
            }

        else:
            return {
                'code': 0,
                'message': 'OK',
                'data': {
                    'id': association['id'],
                    'name': association['name'],
                    'prestige': association['prestige'],
                    'rank': association['rank'],
                    'chair': association['chair'],
                    'deputies': association['deputies'],
                    'members': association['members'],
                }
            }

    ####################################################################################################################
    #
    # Station methods
    #
    ####################################################################################################################

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def station(self, player_id=None):
        self.log.debug('%s /station/%s called' % (cherrypy.request.method, player_id))

        if player_id is None:
            player_id = AvatarManager.get_instance().id
            self.log.debug('Using active player id: %s' % player_id)

        buildings = StationManager.get_instance().get_buildings(player_id)

        result = {}
        for building_id, building_data in buildings.items():
            result[building_id] = {
                'name': building_data['name'],
                'level': building_data['level'],
                'build_in_progress': building_data['build_in_progress'],
                'build_finish_at': int(time.mktime(building_data['build_finish_at'].timetuple())),
                'production_at': int(time.mktime(building_data['production_at'].timetuple())),
                'video_watched': building_data['video_watched'],
            }

        return {
            'code': 0,
            'message': 'OK',
            'data': result,
        }

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def collect(self, user_id=None, building_id=None):
        self.log.debug('%s /collect/%s/%s called' % (cherrypy.request.method, building_id, user_id))
        if cherrypy.request.method == 'OPTIONS':
            return ''

        elif cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        if building_id is not None and int(building_id) not in (7, 8, 9):
            error_msg = 'Can only collect bonus from building_ids: 7, 8, 9. Requested: %s' % building_id
            self.log.error(error_msg)
            return {'code': 1, 'message': error_msg, 'data': None}

        manager = CollectManager.get_instance()
        try:
            if building_id is None:
                r = manager.collect_player(user_id)
            else:
                r = manager.collect(building_id, user_id)
        except RailNationClientError as err:
            self.log.error('Error: %s' % str(err))
            return {
                'code': 1,
                'message': str(err),
                'data': None
            }
        else:
            return {
                'code': 0,
                'message': 'OK',
                'data': r
            }

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def autocollect(self, action=None):
        self.log.debug('%s /autocollect/%s called' % (cherrypy.request.method, action))
        if cherrypy.request.method == 'OPTIONS':
            return ''

        elif cherrypy.request.method == 'GET':
            manager = CollectManager.get_instance()
            if action is None:
                return {
                    'code': 0,
                    'message': 'OK',
                    'data': manager.auto_collect
                }

            elif action == 'stats':
                return {
                    'code': 0,
                    'message': 'OK',
                    'data': manager.stats
                }

            elif action == 'history':
                return {
                    'code': 0,
                    'message': 'OK',
                    'data': manager.history[-10:]
                }

            else:
                return {
                    'code': 1,
                    'message': 'Bad request: GET /autocollect/%s' % action,
                    'data': None
                }

        elif cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        if action == 'enable':
            manager = CollectManager.get_instance()
            manager.auto_collect = True
            return {
                'code': 0,
                'message': 'OK',
                'data': manager.auto_collect
            }

        elif action == 'disable':
            manager = CollectManager.get_instance()
            manager.auto_collect = False
            return {
                'code': 0,
                'message': 'OK',
                'data': manager.auto_collect
            }

        else:
            return {
                'code': 1,
                'message': 'Bad request: POST /autocollect/%s' % action,
                'data': None
            }

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def build(self, building_id):
        self.log.debug('%s /build/%s called' % (cherrypy.request.method, building_id))
        if cherrypy.request.method == 'OPTIONS':
            return ''

        elif cherrypy.request.method == 'DELETE':
            if not building_id.isdigit() or int(building_id) not in range(10):
                return {
                    'code': 1,
                    'message': 'Bad building ID: %s' % building_id,
                    'data': None
                }
            else:
                return {
                    'code': 0,
                    'message': 'OK',
                    'data': StationManager.get_instance().cancel_upgrade(building_id)
                }

        elif cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        if not building_id.isdigit() or int(building_id) not in range(10):
            return {
                'code': 1,
                'message': 'Bad building ID: %s' % building_id,
                'data': None
            }

        StationManager.get_instance().upgrade_building(building_id)
        return {
            'code': 0,
            'message': 'OK',
            'data': True
        }

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def buildqueue(self, action=None):
        self.log.debug('%s /buildqueue called' % cherrypy.request.method)
        if cherrypy.request.method == 'OPTIONS':
            return ''

        elif cherrypy.request.method == 'GET':
            manager = CollectManager.get_instance()
            if action is None:
                return {
                    'code': 0,
                    'message': 'OK',
                    'data': StationManager.get_instance().build_queue
                }

            else:
                return {
                    'code': 1,
                    'message': 'Bad request: GET /buildqueue/%s' % action,
                    'data': None
                }

        elif cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError('405 Method Not Allowed')

        if action == 'clear':
            StationManager.get_instance().build_queue = []
            return {
                'code': 0,
                'message': 'OK',
                'data': StationManager.get_instance().build_queue
            }



