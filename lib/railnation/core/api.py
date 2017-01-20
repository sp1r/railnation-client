#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import cherrypy
import json

from railnation.managers.account import AccountManager
from railnation.core.common import (
    log,
    IS_PY3
)


class RailNationClientAPIv1:

    def __init__(self):
        self.log = log.getChild('APIv1')

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
            request = json.loads(raw_body)
        except ValueError:
            error_msg = 'Request body is not a json object.'
            self.log.error(error_msg)
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

        if not manager.authenticated:
            manager.login(username, password)
        else:
            self.log.warning('Game session already authenticated')
            return {'code': 0, 'message': 'Already authenticated', 'data': True}

        if manager.authenticated:
            self.log.debug('Auth success')
            return {'code': 0, 'message': 'OK', 'data': True}
        else:
            self.log.debug('Auth failed')
            return {'code': 1, 'message': 'Auth failed', 'data': False}

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def worlds(self):
        self.log.debug('%s /worlds called' % cherrypy.request.method)
        manager = AccountManager.get_instance()

        if not manager.authenticated:
            self.log.error('Cannot list worlds before authentication')
            return {'code': 1, 'message': 'Not authenticated', 'data': None}

        response = []

        self.log.debug('Listing avatars')
        for avatar_id, avatar_data in manager.avatars.items():
            self.log.debug('Processing avatar: %s' % avatar_id)
            self.log.debug('Avatar`s world id: %s' % avatar_data['consumersId'])
            try:
                avatar_info = manager.avatars_details[int(avatar_id)]
            except KeyError:
                self.log.critical('Avatar details not found. Error in initialization!')
                return {'code': 2, 'message': 'Initialization error', 'data': None}
            try:
                world_info = manager.worlds[int(avatar_data['consumersId'])]
            except KeyError:
                self.log.critical('World data not found. Error in initialization!')
                return {'code': 2, 'message': 'Initialization error', 'data': None}

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

        self.log.debug('Returning %s worlds' % len(response))
        return {'code': 0, 'message': 'OK', 'data': response}

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def join(self, world_id):
        self.log.debug('%s /join/%s called' % (cherrypy.request.method, world_id))
        manager = AccountManager.get_instance()

        manager.join_world(world_id)

        if manager.in_game:
            return {'code': 0, 'message': 'OK', 'data': True}
        else:
            return {'code': 1, 'message': 'Error', 'data': False}


