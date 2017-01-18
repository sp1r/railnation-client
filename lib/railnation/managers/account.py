#!/usr/bin/env python
# -*- coding:  utf-8 -*-

# import html.parser
import logging
import random

from railnation.config import (
    BASE_URL,
    LOBBY_URL,
    MELLON_CONFIG,
    XDM_CONFIG,
)
from railnation.core.server import session
from railnation.core.errors import RailNationInitializationError


msid_chars = ('1', '2', '3', '4', '5', '6', '7', '8', '9',
              'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
              'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v')


def _get_random_msid():
    random.seed()
    return ''.join([random.choice(msid_chars) for x in range(26)])


# class HTMLAttributeSearch(html.parser.HTMLParser):
#     """
#     Find attribute value by tag type and id.
#     """
#
#     def error(self, message):
#         self.log.error('Parsing error: %s' % message)
#
#     def __init__(self, tag_to_find,
#                  filter_by_attr, filter_attr_value, attr_to_extract):
#         html.parser.HTMLParser.__init__(self)
#         self.log = logging.getLogger('HTMLAttributeSearch')
#         self.interesting_tag = tag_to_find
#         self.filter = filter_by_attr
#         self.filter_value = filter_attr_value
#         self.target = attr_to_extract
#         self.result = None
#
#     def handle_starttag(self, tag, attrs):
#         if tag == self.interesting_tag:
#             attributes = {k: v for k, v in attrs}
#             try:
#                 if attributes[self.filter] == self.filter_value:
#                     self.result = attributes[self.target]
#             except KeyError:
#                 pass
#
#
# class GrepWorldsInformation(html.parser.HTMLParser):
#     """
#     More complex logic to extract worlds information
#     """
#
#     def error(self, message):
#         self.log.error('Parsing error: %s' % message)
#
#     def __init__(self):
#         html.parser.HTMLParser.__init__(self)
#         self.log = logging.getLogger('GrepWorldsInformation')
#         self.in_target_block = False
#         self.grep_data = False
#         self.grep_data_into = ''
#         self.current_world = {}
#         self.results = []
#
#     def handle_starttag(self, tag, attrs):
#         if tag == 'div':
#             attributes = {k: v for k, v in attrs}
#             try:
#                 if attributes['class'] == 'gameWorldsForLogin':
#                     self.in_target_block = True
#                 elif attributes['class'] == 'gameWorldsForRegistration':
#                     self.in_target_block = False
#             except KeyError:
#                 pass
#
#         try:
#
#             if self.in_target_block:
#                 if tag == 'li':
#                     attributes = {k: v for k, v in attrs}
#                     if attributes['class'] == 'world-name':
#                         self.grep_data = True
#                         self.grep_data_into = 'name'
#                     elif attributes['class'] == 'world-status':
#                         self.grep_data = True
#                         self.grep_data_into = 'era'
#                     elif attributes['class'] == 'world-population':
#                         self.grep_data = True
#                         self.grep_data_into = 'population'
#
#                 elif tag == 'img':
#                     attributes = {k: v for k, v in attrs}
#                     if 'statuses' in attributes['src']:
#                         self.current_world['status'] = attributes['src'].split('/')[-1].split('.')[0]
#
#                     elif 'maps' in attributes['src']:
#                         self.current_world['map'] = attributes['src'].split('/')[-1].split('.')[0]
#
#                 elif tag == 'a':
#                     attributes = {k: v for k, v in attrs}
#                     if attributes['class'] == 'one-click':
#                         self.current_world['link'] = attributes['href']
#                         self.results.append(self.current_world)
#                         self.current_world = {}
#
#         except KeyError:
#             pass
#
#     def handle_data(self, data):
#         if self.grep_data:
#             self.current_world[self.grep_data_into] = data.strip()
#             self.grep_data = False


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
        self.mellon_config = {
            'url': 'http://mellon-rn.traviangames.com',
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

    #     self.log.debug('Knock-knock on rail-nation lobby')
    #     response = session.get(LOBBY_URL)
    #     if len(response.history) > 0:
    #         self.log.debug('Cannot enter lobby. Authenticate first?')
    #     else:
    #         self.log.info('Joined Rail-Nation Lobby')
    #         self.authenticated = True
    #
    # def _load_home_page(self):
    #     home_url = '%s/home/' % BASE_URL
    #     self.log.debug('Loading home page: %s' % home_url)
    #     response = session.get(home_url)
    #     self.log.debug("Result: %s %s" % (response.status_code,
    #                                       response.reason))
    #
    #     if response.status_code != 200:
    #         self.log.critical("Failed to download home page (%s)" % home_url)
    #         self.log.critical("Response: %s" % response.text)
    #         raise RailNationInitializationError("Failed to download home page. See logs for details.")

    def _get_mellon_url(self, action):
        url = self.mellon_config['url']
        if action == 'login':
            url += '/authentication/login'

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

        self.log.debug("Sending login data to server")
        response = session.post(auth_url,
                                data=login_data,
                                params={
                                    'msname': 'msid',
                                    'msid': _get_random_msid()
                                })
        self.log.debug("Code: %s %s" % (response.status_code,
                                        response.reason))

        if response.status_code != 200:
            self.log.critical("Authentication failed.")
            self.log.critical("Response: %s" % response.text)
            raise RailNationInitializationError("Could not authenticate. See logs for details.")

        self.log.info('Successfully logged in to the game.')
        self.log.trace(response.text)

        # grep redirect url
        try:
            s = response.text.index("parent.bridge.redirect({url: '")
            e = response.text.index("'", s+30)
        except ValueError:
            raise RailNationInitializationError('Cannot parse redirect url from login response!')
        else:
            redirect_url = response.text[s+30, e]

        self.log.debug('Got redirect url: %s' % redirect_url)

        try:
            msid_cookie = {k: v for k, v in [p.split('=') for p in redirect_url.split('&')[1].split('?')]}['msid']
        except KeyError:
            raise RailNationInitializationError('Cannot parse msid from redirect url in login response!')

        self.log.debug('Got new msid cookie: %s' % msid_cookie)
        session.cookies.update({'msid': msid_cookie})

        self.log.debug('Entering Lobby...')
        response = session.get(redirect_url)



