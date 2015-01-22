# -*- coding:utf-8 -*-
"""Клиент сервера railnation"""

import hashlib
import json
import requests
import requests.exceptions
import time
import html.parser

from raillib.errors import (
    ConnectionProblem,
    NotAuthenticated,
)

# I believe this won`t change every day
BASE_URL = 'www.rail-nation.com'

sam_config = {}

CLIENT_CHECKSUM = 'ea24d4af2c566004782f750f940615e5'  # hardcoded in flash-app
MAX_RECONNECT = 5
MAX_WAIT = 3


class Client:
    def __init__(self):
        self.authenticated = False
        self.worlds = {}
        self.rpc_url = ''
        self.webkey = ''
        self.session = requests.Session()
        self.session.headers.update({
            'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/36.0.1985.125 Safari/537.36'
        })

        self.player_id = 'False'
        self.properties = {}
        self.client_info = {}
        self.language = ''

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
                                      timeout=MAX_WAIT)

            except requests.exceptions.ConnectionError:
                time.sleep(0.25)

            except requests.exceptions.Timeout:
                pass

            # если нет ошибок - возвращаем ответ
            else:
                return r.json()

        # более чем MAX_RECONNECT неудачных попыток соединения считаем
        # критической ошибкой и выходим
        else:
            raise ConnectionProblem('Too many connection failures (%s)'
                                    % MAX_RECONNECT)

    def authenticate(self, login, password):
        """
        Authenticate this client
        """
        # загружаем конфигурацию SAM
        sam_url = 'http://%s/js/sam.config.php' % BASE_URL
        response = self.session.get(sam_url)

        if response.status_code != 200:
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

        # загружаем фрейм с формой ввода пароля
        response = self.session.get(self.get_link('login'))

        # находим элемент с id="loginForm" и сохраняем его параметр action
        parser = HTMLAttributeSearch('form', 'id', 'loginForm', 'action')
        parser.feed(response.text)
        login_target = parser.result

        login_data = {
            'className': 'login ',
            'email': login,
            'password': password,
            'remember_me': 0,
        }

        # отправляем логин и пароль на сервер
        response = self.session.post(login_target, data=login_data)

        # проверяем успешна ли авторизация
        parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
        parser.feed(response.text)

        if parser.result is not None:
            self.authenticated = True
        else:
            return

        self.session.headers.update(
            {
                'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6'
            }
        )

        # загружаем фрейм с выбором id мира для входа;
        # сервер косячит, он кодирует кириллицу в юникод, но не устанавливает
        # значение charset=utf-8 в заголовке Content-type, поэтому
        # придется прибегнуть к военной хитрости
        response = self.session.get(self.get_link('external-avatar-list'),
                                    stream=True)

        frame = str(response.raw.read(), 'utf-8')

        # ищем миры, в которых у нас есть персонажи
        parser = GrepWorldsInformation()
        parser.feed(frame)

        self.worlds = {w['id']: World(w) for w in parser.results}

    def get_worlds(self):
        if not self.authenticated:
            return []

        return self.worlds.values()

    def enter_world(self, world_id):
        if not self.authenticated:
            return None

        world_data = {
            'world': world_id,
        }

        # отправляем id мира на сервер
        response = self.session.post(self.worlds[world_id].action,
                                     data=world_data)

        # в ответе находим ссылку класса forwardLink и сохраняем href
        parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
        parser.feed(response.text)
        auth_link = parser.result

        self.rpc_url, self.webkey = auth_link.split('?key=')
        self.rpc_url += 'rpc/flash.php'

        # авторизуемся через эту ссылку (получаем куку в сессию)
        response = self.session.get(auth_link)

        return response.status_code == 200

    def get_link(self, action):
        """
        Повторяет функционал из http://www.rail-nation.com/js/sam.js
        """
        target = "%s/iframe/%s/applicationId/%s/applicationCountryId/%s" \
                 "/applicationInstanceId/%s/userParam/undefined/" % \
                 (sam_config['url'],
                  action,
                  sam_config['applicationId'],
                  sam_config['applicationCountryId'],
                  sam_config['applicationInstanceId'])
        return target


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
        self.current_world = {
            'target': None,
            'online': False
        }
        self.results = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            attributes = {k: v for k, v in attrs}
            try:
                if attributes['id'] == 'ownAvatarHeadline':
                    self.in_target_block = True
                elif attributes['id'] == 'newServerHeadline':
                    self.in_target_block = False
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
                    elif attributes['class'] == 'serverAgeColumn':
                        self.grep_data = True
                        self.grep_data_into = 'age'
                    elif 'status-online' in attributes['class']:
                        self.current_world['online'] = True
                except KeyError:
                    pass
                except TypeError:
                    pass

        if tag == 'input' and self.in_target_block:
            attributes = {k: v for k, v in attrs}
            try:
                if attributes['id'] == 'loginAvatarWorldInput':
                    self.current_world['id'] = attributes['value']
                    self.results.append(self.current_world)
                    self.current_world = {
                        'target': None,
                        'online': False
                    }
            except KeyError:
                pass

        if tag == 'form' and self.in_target_block:
            attributes = {k: v for k, v in attrs}
            try:
                if attributes['class'] == 'loginAvatarForm':
                    self.current_world['action'] = attributes['action']
            except KeyError:
                pass

        if tag == 'img' and self.in_target_block:
            attributes = {k: v for k, v in attrs}
            try:
                self.current_world['flag'] = attributes['src']
            except KeyError:
                pass

        if tag == 'span' and self.in_target_block:
            attributes = {k: v for k, v in attrs}
            try:
                if attributes['class'] == 'playersActive':
                    self.grep_data = True
                    self.grep_data_into = 'players_active'
                elif attributes['class'] == 'playersOnline':
                    self.grep_data = True
                    self.grep_data_into = 'players_online'
            except KeyError:
                pass

    def handle_data(self, data):
        if self.grep_data:
            self.current_world[self.grep_data_into] = data
            self.grep_data = False


class World(object):
    def __init__(self, world_data):
        self.id = world_data['id']
        self.name = world_data['name']
        self.flag = world_data['flag'].split('/')[-1].split('.')[0]
        self.age = world_data['age']
        self.era = int(world_data['era'].split()[1])

        self.online = world_data['online']
        self.players_active = world_data['players_active'].split()[0]
        self.players_online = world_data['players_online'].split()[0].strip('(')

        self.last_login = world_data['last_login']

        self.action = world_data['action']