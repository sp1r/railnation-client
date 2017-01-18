#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import logging
import cherrypy

from railnation.managers.account import AccountManager


class RailNationClientAPIv1:

    def __init__(self):
        self.log = logging.getLogger('RailNationAPIv1')

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def login(self, username, password):
        self.log.debug('Logging in as: %s' % username)
        manager = AccountManager.get_instance()

        if not manager.authenticated:
            manager.login(username, password)

        if manager.authenticated:
            self.log.debug('Auth success')
            return {'result': 'OK'}
        else:
            self.log.debug('Auth failed')
            return {'result': 'Error'}

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def worlds(self):
        self.log.debug('Listing worlds')
        manager = AccountManager.get_instance()

        lobby_info = manager.get_lobby_info()
