# -*- coding:utf-8 -*-
"""Клиент сервера railnation"""

import hashlib
import json
import requests
import requests.exceptions
import time
import sys
import getpass
import html.parser
import logging

# from railnation.core.railnation_log import log
# log.debug('Loading module: Client')

from railnation.core.railnation_errors import (
    ConnectionProblem,
    NotAuthenticated,
)

# I believe this won`t change every day
BASE_URL = 'www.rail-nation.com'

sam_config = {}

CLIENT_CHECKSUM = 'ea24d4af2c566004782f750f940615e5'  # hardcoded in flash-app
MAX_RECONNECT = 10


class Client:
    def __init__(self):
        self.rpc_url = ''
        self.webkey = ''
        self.session = requests.Session()
        self.session.headers.update({
            'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/36.0.1985.125 Safari/537.36'
        })

        self.log = logging.Logger('debug-log')

        self.player_id = 'False'
        self.properties = {}
        self.client_info = {}
        self.language = ''

    @property
    def is_authorized(self):
        return self.rpc_url == ''

    def produce(self, interface, method, params):
        """
        Обращение к серверу.

        :param interface: имя интерфейса
        :type interface: str
        :param method: имя метода
        :type method: str
        :param params: параметры вызова
        :type params: list
        :return: ответ сервера
        :rtype: dict
        """
        self.log.debug('Trying: %s %s %s' % (interface, method, params))
        target = {'interface': interface,
                  'method': method}
        payload = {'ckecksum': CLIENT_CHECKSUM,
                   'client': 1,
                   'hash': _make_hash(params),
                   'parameters': params}

        connect = 0
        while connect < MAX_RECONNECT:
            connect += 1
            try:
                r = self.session.post(self.rpc_url,
                                      params=target,
                                      data=json.dumps(payload),
                                      timeout=5)

            except requests.exceptions.ConnectionError:
                self.log.warning('Connection problems.')
                time.sleep(1)

            except requests.exceptions.Timeout:
                self.log.warning('No response from server (timeout).')

            # если нет ошибок - возвращаем ответ
            else:
                self.log.debug('Response: %s Error: %s Content: %s' %
                          (r.status_code, r.reason, r.text))
                return r.json()

        # более чем 10 неудачных попыток соединения считаем критической
        # ошибкой и выходим
        else:
            self.log.critical('Too much connection errors. Will now exit.')
            sys.exit(1)

    def authenticate(self):
        """
        Authenticate this client
        """
        print('Connecting to www.rail-nation.com...')
        # загружаем конфигурацию SAM
        sam_url = 'http://%s/js/sam.config.php' % BASE_URL
        self.log.debug('Downloading SAM config...')
        self.log.debug('SAM config url: %s' % sam_url)
        response = self.session.get(sam_url)
        self.log.debug('Response: %s Message: %s' % (response.status_code,
                                                response.reason))

        if response.status_code != 200:
            self.log.critical("Error while getting SAM config from server.")
            raise ConnectionProblem("Could not download SAM config.")

        # парсим строки вида:
        # samConfig['applicationId'] = 'railnation';
        for line in response.iter_lines():
            # iter_lines() возвращает объекты типа <bytes>
            line = str(line)
            if line.startswith('b"samConfig['):
                fields = line.split("'")
                key, value = fields[1], fields[3]
                sam_config[key] = value
                self.log.debug('SAM item: %s = %s' % (key, sam_config[key]))

        # загружаем фрейм с формой ввода пароля
        self.log.debug('Requesting login frame...')
        response = self.session.get(self.get_link('login'))
        self.log.debug('Response: %s Message: %s' % (response.status_code,
                                                response.reason))

        # находим элемент с id="loginForm" и сохраняем его параметр action
        parser = HTMLAttributeSearch('form', 'id', 'loginForm', 'action')
        parser.feed(response.text)
        login_target = parser.result
        self.log.debug('Login form submit url: %s' % login_target)

        # спрашиваем имя и пароль у пользователя
        username = input("Enter your email (login): ")
        self.log.info('Trying to login. User: %s' % username)
        password = getpass.getpass("Password for %s: " % username)

        login_data = {
            'className': 'login ',
            'email': username,
            'password': password,
            'remember_me': 0,
        }

        # отправляем логин и пароль на сервер
        self.log.debug('Sending credentials...')
        response = self.session.post(login_target, data=login_data)
        self.log.debug('Response: %s Message: %s' % (response.status_code,
                                                response.reason))

        # проверяем успешна ли авторизация
        parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
        parser.feed(response.text)
        if parser.result is None:
            self.log.critical('Username or password is incorrect.')
            raise NotAuthenticated('You entered wrong username and password.')

        self.session.headers.update({'Accept-Language':
                                       'en-US,en;q=0.8,ru;q=0.6'})

        # загружаем фрейм с выбором id мира для входа;
        # сервер косячит, он кодирует кириллицу в юникод, но не устанавливает
        # значение charset=utf-8 в заголовке Content-type, поэтому
        # придется прибегнуть к военной хитрости
        self.log.debug('Requesting world selection frame...')
        response = self.session.get(self.get_link('external-avatar-list'),
                                      stream=True)
        self.log.debug('Response: %s Message: %s' % (response.status_code,
                                                response.reason))

        frame = str(response.raw.read(), 'utf-8')

        # ищем миры, в которых у нас есть персонажи
        parser = GrepWorldsInformation()
        parser.feed(frame)

        table = '[%-3s] %-20s %-8s %-20s'
        print('List of your games:')
        print(table % ('ID', 'Name', 'Era', 'Last login'))
        for world, data in parser.result.items():
            print(table % (world,
                                                   data['name'],
                                                   data['era'],
                                                   data['last_login']))

        world_id = int(input('Choose world ID to enter: '))

        # ищем элементы класса loginAvatarForm и сохраняем их параметр action
        parser = HTMLAttributeSearch('form', 'class', 'loginAvatarForm', 'action')
        parser.feed(frame)
        world_target = parser.result
        self.log.debug('World selection form submit url: %s' % world_target)

        world_data = {
            'world': world_id,
        }

        # отправляем id мира на сервер
        self.log.info('Entering world %s...' % world_data['world'])
        response = self.session.post(world_target, data=world_data)
        self.log.debug('Response: %s Message: %s' % (response.status_code,
                                                response.reason))

        # в ответе находим ссылку класса forwardLink и сохраняем href
        parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
        parser.feed(response.text)
        auth_link = parser.result

        self.rpc_url, self.webkey = auth_link.split('?key=')
        self.rpc_url += 'rpc/flash.php'
        self.log.debug('RPC url: %s' % self.rpc_url)
        self.log.debug('Web key: %s' % self.webkey)

        # авторизуемся через эту ссылку (получаем куку в сессию)
        self.log.debug('Authorizing via link: %s' % auth_link)
        response = self.session.get(auth_link)
        self.log.debug('Response: %s Message: %s' % (response.status_code,
                                                response.reason))

    def get_link(self, action):
        """
        Повторяет функционал из http://www.rail-nation.com/js/sam.js
        """
        self.log.debug('Constructing url for %s frame' % action)
        target = "%s/iframe/%s/applicationId/%s/applicationCountryId/%s" \
                 "/applicationInstanceId/%s/userParam/undefined/" % \
                 (sam_config['url'],
                  action,
                  sam_config['applicationId'],
                  sam_config['applicationCountryId'],
                  sam_config['applicationInstanceId'])
        self.log.debug('Link for %s frame is: %s' % (action, target))
        return target

    def load_parameters(self):
        self.player_id = str(self.produce('AccountInterface',
                             'is_logged_in',
                             [self.webkey])['Body'])
        if self.player_id == 'False':
            # log.critical('Got "False" instead of player ID while loading!')
            raise NotAuthenticated('Error while authenticating you.')

        # log.debug('Web Client authenticated.')

        r = self.produce('PropertiesInterface',
                           'getData',
                           [])['Body']

        self.properties = r['properties']
        self.properties['client'] = r['client']

        self.client_info = self.produce('KontagentInterface',
                                     'getData',
                                     [])['Body']

        self.language = str(self.produce('AccountInterface',
                                      'getLanguage',
                                      [])['Body'])

def _quote(item):
    """
    Правильная расстановка кавычек, пробелов и скобочек в стиле json.
    Необходима для того, чтобы md5-сумма строки параметров вычислялась
    правильно.

    :param item: объект любого типа
    :type item: str or dict or list of bool or int
    :return: строка с правильно расставленными кавычками
    :rtype: str
    """
    if isinstance(item, list):
        return '[' + ','.join([_quote(i) for i in item]) + ']'
    elif isinstance(item, dict):
        return '{' + ','.join([_quote(k) + ':' + _quote(v)
                               for k, v in item.items()]) + '}'
    elif isinstance(item, str):
        return '"' + item + '"'
    else:
        return str(item).lower()


def _make_hash(item):
    """Сокращение"""
    return hashlib.md5(_quote(item).encode("utf-8")).hexdigest()


###############################################################################
# Парсеры html
class HTMLAttributeSearch(html.parser.HTMLParser):
    """
    We need to locate some attributes in html-pages we got from server
    """
    def __init__(self, tag_to_find,
                 filter_by_attr, filter_attr_value, attr_to_extract):
        html.parser.HTMLParser.__init__(self)
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
    """More complex logic to extract worlds information"""
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.in_target_block = False
        self.grep_data = False
        self.grep_data_into = ''
        self.current_world = {}
        self.result = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            attributes = {k: v for k, v in attrs}
            try:
                if attributes['id'] == 'avatarListContainer':
                    self.in_target_block = True
            except KeyError:
                pass
            if self.in_target_block:
                try:
                    if attributes['class'] == 'serverNameLabel':
                        self.grep_data = True
                        self.grep_data_into = 'name'
                    elif attributes['class'] == 'serverEraLabel':
                        self.grep_data = True
                        self.grep_data_into = 'era'
                    elif attributes['class'] == 'loginColumn':
                        self.grep_data = True
                        self.grep_data_into = 'last_login'
                except KeyError:
                    pass
        if tag == 'input' and self.in_target_block:
            attributes = {k: v for k, v in attrs}
            try:
                if attributes['id'] == 'loginAvatarWorldInput':
                    self.result[attributes['value']] = self.current_world
                    self.current_world = {}
            except KeyError:
                pass

    def handle_data(self, data):
        if self.grep_data:
            self.current_world[self.grep_data_into] = data
            self.grep_data = False