#-*- coding: utf-8 -*-
"""Модуль аутентификации"""

import getpass
import html.parser

from railnation.core.railnation_globals import log

# I believe this won`t change every day
BASE_URL = 'www.rail-nation.com'

sam_config = {}


def authorize(client):
    """
    Проводит аутентификацию

    :param client: класс для общения с игрой
    :type client: railnation.core.railnation_client.Client
    """
    # загружаем конфигурацию SAM
    sam_url = 'http://%s/js/sam.config.php' % BASE_URL
    log.debug('Downloading SAM config...')
    log.debug('SAM config url: %s' % sam_url)
    response = client.session.get(sam_url)
    log.debug('Response: %s Message: %s' % (response.status_code,
                                            response.reason))

    if response.status_code != 200:
        log.critical("Error while getting SAM config from server.")
        print("Connection problems. Will now exit.")
        exit(0)

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

    # запрашиваем логин/пароль от учетной записи
    username, password = console_login()

    log.info('Trying to login. User: %s' % username)

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

    # загружаем фрейм с выбором id мира для входа
    log.debug('Requesting world selection frame...')
    response = client.session.get(_get_link('external-avatar-list'))
    log.debug('Response: %s Message: %s' % (response.status_code,
                                                 response.reason))

    # ищем элементы с id=loginAvatarWorldInput и сохраняем их параметр value
    parser = HTMLAttributeSearch('input', 'id', 'loginAvatarWorldInput', 'value')
    parser.feed(response.text)
    world_id = parser.result
    log.debug('World id to enter: %s' % world_id)

    # ищем элементы класса loginAvatarForm и сохраняем их параметр action
    parser = HTMLAttributeSearch('form', 'class', 'loginAvatarForm', 'action')
    parser.feed(response.text)
    world_target = parser.result
    log.debug('World selection form submit url: %s' % world_target)

    # TODO: add 'choose world' feature here.
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

    client.session.headers.update({'content-type': 'application/json'})

    client.player_id = client.produce('AccountInterface',
                                      'is_logged_in',
                                      [client.webkey])['Body']
    if not client.player_id:
        print('Cannot log in to the game.')
        exit(1)


def console_login():
    print("Please enter you credentials.")
    name = input("Enter name (email): ")
    password = getpass.getpass("Password for %s: " % name)
    return name, password


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
# Парсер html
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
            if self.filter in attributes and \
                    attributes[self.filter] == self.filter_value:
                self.result = attributes[self.target]