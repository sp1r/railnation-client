#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import cherrypy
import json
import time
import datetime

from railnation.core.common import (
    log,
    IS_PY3
)
from railnation.core.errors import (
    RailNationClientError
)
from railnation.managers.account import AccountManager
from railnation.managers.avatar import AvatarManager
from railnation.managers.association import AssociationManager
from railnation.managers.collect import CollectManager
from railnation.managers.resources import ResourcesManager
from railnation.managers.station import StationManager


class RailNationClientAPIv1:

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
                response.append({
                    'avatarName': avatar_data['avatarName'],
                    'avatarId': avatar_data['avatarIdentifier'],
                    'country': avatar_data['country'],
                    'isBanned': avatar_data['isBanned'],
                    'isSuspended': avatar_data['isSuspended'],
                    'playerPrestige': avatar_info['playerPrestige'],
                    'playerRank': avatar_info['playerRank'],
                    'cityName': manager.city_names[int(world_info['cityNamesPackage'])][avatar_info['cityId']],
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
            association = AssociationManager.get_instance(association_id)

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
                    'id': association.id,
                    'name': association.name,
                    'prestige': association.prestige,
                    'rank': association.rank,
                    'chair': association.chair,
                    'deputies': association.deputies,
                    'members': association.members,
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

