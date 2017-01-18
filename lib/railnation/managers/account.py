#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import html.parser
import logging

from lib.railnation.config import (
    BASE_URL,
    LOBBY_URL,
    MELLON_CONFIG,
    XDM_CONFIG,
)
from railnation.core.server import session
from railnation.core.errors import RailNationInitializationError


class HTMLAttributeSearch(html.parser.HTMLParser):
    """
    Find attribute value by tag type and id.
    """

    def error(self, message):
        self.log.error('Parsing error: %s' % message)

    def __init__(self, tag_to_find,
                 filter_by_attr, filter_attr_value, attr_to_extract):
        html.parser.HTMLParser.__init__(self)
        self.log = logging.getLogger('HTMLAttributeSearch')
        self.interesting_tag = tag_to_find
        self.filter = filter_by_attr
        self.filter_value = filter_attr_value
        self.target = attr_to_extract
        self.result = None

    def handle_starttag(self, tag, attrs):
        if tag == self.interesting_tag:
            attributes = {k: v for k, v in attrs}
            try:
                if attributes[self.filter] == self.filter_value:
                    self.result = attributes[self.target]
            except KeyError:
                pass


class GrepWorldsInformation(html.parser.HTMLParser):
    """
    More complex logic to extract worlds information
    """

    def error(self, message):
        self.log.error('Parsing error: %s' % message)

    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.log = logging.getLogger('GrepWorldsInformation')
        self.in_target_block = False
        self.grep_data = False
        self.grep_data_into = ''
        self.current_world = {}
        self.results = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            attributes = {k: v for k, v in attrs}
            try:
                if attributes['class'] == 'gameWorldsForLogin':
                    self.in_target_block = True
                elif attributes['class'] == 'gameWorldsForRegistration':
                    self.in_target_block = False
            except KeyError:
                pass

        try:

            if self.in_target_block:
                if tag == 'li':
                    attributes = {k: v for k, v in attrs}
                    if attributes['class'] == 'world-name':
                        self.grep_data = True
                        self.grep_data_into = 'name'
                    elif attributes['class'] == 'world-status':
                        self.grep_data = True
                        self.grep_data_into = 'era'
                    elif attributes['class'] == 'world-population':
                        self.grep_data = True
                        self.grep_data_into = 'population'

                elif tag == 'img':
                    attributes = {k: v for k, v in attrs}
                    if 'statuses' in attributes['src']:
                        self.current_world['status'] = attributes['src'].split('/')[-1].split('.')[0]

                    elif 'maps' in attributes['src']:
                        self.current_world['map'] = attributes['src'].split('/')[-1].split('.')[0]

                elif tag == 'a':
                    attributes = {k: v for k, v in attrs}
                    if attributes['class'] == 'one-click':
                        self.current_world['link'] = attributes['href']
                        self.results.append(self.current_world)
                        self.current_world = {}

        except KeyError:
            pass

    def handle_data(self, data):
        if self.grep_data:
            self.current_world[self.grep_data_into] = data.strip()
            self.grep_data = False


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
        self.log = logging.getLogger('AccountManager')
        self.log.debug('Initializing...')
        self.authenticated = False
        self.username = None

        self.log.debug('Knock-knock on rail-nation lobby')
        response = session.get(LOBBY_URL)
        if len(response.history) > 0:
            self.log.debug('Cannot enter lobby. Authenticate first?')
        else:
            self.log.info('Found previous session.')
            self.authenticated = True

    def login(self, username, password):
        # Load home page
        home_url = '%s/home/' % BASE_URL
        self.log.debug('Loading home page: %s' % home_url)
        response = session.get(home_url)
        self.log.debug("Code: %s %s" % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical("Failed to download home page (%s)" % home_url)
            self.log.critical("Response: %s" % response.text)
            raise RailNationInitializationError("Failed to download home page. See logs for details.")

        # Load Mellon config
        # TODO: read this url from web-page <script> tag
        config_url = '%s/wp-content/themes/railnation/js/mellon/config.php' % BASE_URL
        self.log.debug('Loading Mellon config from: %s' % config_url)
        response = session.get(config_url)
        self.log.debug("Code: %s %s" % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical("Failed to download Mellon config (%s)" % config_url)
            self.log.critical("Response: %s" % response.text)
            raise RailNationInitializationError("Failed to download Mellon config. See logs for details.")

        self.log.debug('Got Mellon config:')
        self.log.debug(response.text)

        # Grep base mellon url:
        try:
            start = response.text.rindex("new MellonUrl(")
        except ValueError:
            self.log.critical("Failed to parse Mellon config.")
            raise RailNationInitializationError("Failed to load Mellon config. See logs for details.")
        else:
            end = response.text.index(")", start)
            self.log.debug('Found url indexes: [%s, %s]' % (start, end))
            mellon_base_url = response.text[start+15:end-1]

        self.log.debug("Found Mellon base url: %s" % mellon_base_url)

        self.log.debug('Trying to login with username: %s' % username)

        # get frame with login form
        auth_url = mellon_base_url + '/authentication/login/'
        for k, v in MELLON_CONFIG.items():
            auth_url += '/%s/%s' % (k, v)

        self.log.debug('Loading login frame from: %s' % auth_url)
        response = session.get(auth_url, params=XDM_CONFIG)
        self.log.debug("Code: %s %s" % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical("Could not download login frame.")
            self.log.critical("Response: %s" % response.text)
            raise RailNationInitializationError("Could not download login frame. See logs for details.")

        # parse received html for tag "form" with id="loginForm" and grep its "action" attribute
        parser = HTMLAttributeSearch('form', 'id', 'login', 'action')
        parser.feed(response.text)
        login_target = parser.result
        self.log.debug('Found login target: %s' % login_target)

        login_data = {
            'submit': 'Login',
            'email': username,
            'password': password,
        }

        # Send login & password
        self.log.debug("Sending login & password to server")
        response = session.post(mellon_base_url + login_target, data=login_data)
        self.log.debug("Code: %s %s" % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical("Authentication failed.")
            self.log.critical("Response: %s" % response.text)
            raise RailNationInitializationError("Could not authenticate. See logs for details.")

        # It everything is ok - we will get a frame with worlds
        self.log.info('Successfully logged in to the game.')
        self.log.debug(response.text)

    def get_lobby_info(self):
        self.log.debug('Trying railnation lobby')


