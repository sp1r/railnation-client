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
            raise cherrypy.HTTPError('400 Bad Request', error_msg)

        try:
            username = request['username']
            password = request['password']
        except KeyError:
            error_msg = 'Request body is missing keys: "username", "password"'
            self.log.error(error_msg)
            raise cherrypy.HTTPError('400 Bad Request', error_msg)

        self.log.debug('Continue as: %s' % username)
        manager = AccountManager.get_instance()

        if not manager.authenticated:
            manager.login(username, password)

        if manager.authenticated:
            self.log.debug('Auth success')
            return {'code': 0, 'data': True}
        else:
            self.log.debug('Auth failed')
            return {'code': 0, 'data': False}

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def worlds(self):
        self.log.debug('Listing worlds')
        manager = AccountManager.get_instance()

        response = []

        for avatar in manager.avatars.values():
            info = manager.avatars_details[avatar['avatarIdentifier']]
            world = manager.worlds[avatar['consumersId']]

            response.append({
                'avatarName': avatar['avatarName'],
                'avatarId': avatar['avatarIdentifier'],
                'country': avatar['country'],
                'isBanned': avatar['isBanned'],
                'isSuspended': avatar['isSuspended'],
                'playerPrestige': info['playerPrestige'],
                'playerRank': info['playerRank'],
                'cityName': manager.city_names[world['cityNamesPackage']][info['cityId']],
                'cityLevel': info['cityLevel'],
                'associationName': info['associationName'],
                'associationPrestige': info['associationPrestige'],
                'associationRank': info['associationRank'],
                'lastLogin': info['lastLogin'],
                'era': world['era'],
                'eraDay': world['eraDay'],
                'eraTimeLapsed': world['eraTimeLapsed'],
                'eraTimeLeft': world['eraTimeLeft'],
                'playersOnline': world['playersOnline'],
                'playersActive': world['playersActive'],
                'playersRegistered': world['playersRegistered'],
                'scenario': world['scenario'],
                'worldName': world['worldName'],
                'worldId': world['consumersId']
            })

        return {'code': 0, 'data': response}


