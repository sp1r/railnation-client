#-*- coding: utf-8 -*-
"""Модуль аутентификации"""

import getpass
import html.parser

from railnation.core.railnation_log import log
log.debug('Loading module: Authentication')

from railnation.core.railnation_errors import (
    ConnectionProblem,
    NotAuthenticated,
)

# I believe this won`t change every day
BASE_URL = 'www.rail-nation.com'

sam_config = {}


def authenticate(client):
    """
    Authenticate this client

    :param client: web client object
    :type client: railnation.core.railnation_client.Client
    """
    print('Connecting to www.rail-nation.com...')
    # загружаем конфигурацию SAM
    sam_url = 'http://%s/js/sam.config.php' % BASE_URL
    log.debug('Downloading SAM config...')
    log.debug('SAM config url: %s' % sam_url)
    response = client.session.get(sam_url)
    log.debug('Response: %s Message: %s' % (response.status_code,
                                            response.reason))

    if response.status_code != 200:
        log.critical("Error while getting SAM config from server.")
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
            log.debug('SAM item: %s = %s' % (key, sam_config[key]))

    # загружаем фрейм с формой ввода пароля
    log.debug('Requesting login frame...')
    response = client.session.get(_get_link('login'))
    log.debug('Response: %s Message: %s' % (response.status_code,
                                            response.reason))

    # находим элемент с id="loginForm" и сохраняем его параметр action
    parser = HTMLAttributeSearch('form', 'id', 'loginForm', 'action')
    parser.feed(response.text)
    login_target = parser.result
    log.debug('Login form submit url: %s' % login_target)

    # спрашиваем имя и пароль у пользователя
    username = input("Enter your email (login): ")
    log.info('Trying to login. User: %s' % username)
    password = getpass.getpass("Password for %s: " % username)

    login_data = {
        'className': 'login ',
        'email': username,
        'password': password,
        'remember_me': 0,
    }

    # отправляем логин и пароль на сервер
    log.debug('Sending credentials...')
    response = client.session.post(login_target, data=login_data)
    log.debug('Response: %s Message: %s' % (response.status_code,
                                            response.reason))

    # проверяем успешна ли авторизация
    parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
    parser.feed(response.text)
    if parser.result is None:
        log.critical('Username or password is incorrect.')
        raise NotAuthenticated('You entered wrong username and password.')

    client.session.headers.update({'Accept-Language':
                                   'en-US,en;q=0.8,ru;q=0.6'})

    # загружаем фрейм с выбором id мира для входа;
    # сервер косячит, он кодирует кириллицу в юникод, но не устанавливает
    # значение charset=utf-8 в заголовке Content-type, поэтому
    # придется прибегнуть к военной хитрости
    log.debug('Requesting world selection frame...')
    response = client.session.get(_get_link('external-avatar-list'),
                                  stream=True)
    log.debug('Response: %s Message: %s' % (response.status_code,
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
    log.debug('World selection form submit url: %s' % world_target)

    world_data = {
        'world': world_id,
    }

    # отправляем id мира на сервер
    log.info('Entering world %s...' % world_data['world'])
    response = client.session.post(world_target, data=world_data)
    log.debug('Response: %s Message: %s' % (response.status_code,
                                            response.reason))

    # в ответе находим ссылку класса forwardLink и сохраняем href
    parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
    parser.feed(response.text)
    auth_link = parser.result

    client.rpc_url, client.webkey = auth_link.split('?key=')
    client.rpc_url += 'rpc/flash.php'
    log.debug('RPC url: %s' % client.rpc_url)
    log.debug('Web key: %s' % client.webkey)

    # авторизуемся через эту ссылку (получаем куку в сессию)
    log.debug('Authorizing via link: %s' % auth_link)
    response = client.session.get(auth_link)
    log.debug('Response: %s Message: %s' % (response.status_code,
                                            response.reason))


def _get_link(action):
    """
    Повторяет функционал из http://www.rail-nation.com/js/sam.js
    """
    log.debug('Constructing url for %s frame' % action)
    target = "%s/iframe/%s/applicationId/%s/applicationCountryId/%s" \
             "/applicationInstanceId/%s/userParam/undefined/" % \
             (sam_config['url'],
              action,
              sam_config['applicationId'],
              sam_config['applicationCountryId'],
              sam_config['applicationInstanceId'])
    log.debug('Link for %s frame is: %s' % (action, target))
    return target


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