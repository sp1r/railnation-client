#-*- coding: utf-8 -*-
"""Модуль аутентификации на игровом сервере"""

import getpass
import html.parser

# I believe this won`t change every day
BASE_URL = 'rail-nation.com'

sam_config = {}


def authorize_client(client):
    """
    Проводит аутентификацию

    :param client: игровой клиент
    :type client: railnation.core.railnation_client.Client
    """
    # загружаем конфигурацию SAM
    sam_url = 'http://%s/js/sam.config.php' % BASE_URL

    client.log.debug('Downloading SAM config...')
    client.log.debug('SAM config url: %s' % sam_url)
    response = client.engine.session.get(sam_url)
    client.log.debug('Response: %s Error: %s' % (response.status_code,
                                                 response.reason))

    if response.status_code != 200:
        print("Error while getting SAM config from server.")
        print("Check your internet connection. Will now exit.")
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
            client.log.debug('SAM item: %s = %s' % (key, sam_config[key]))

    # получаем логин/пароль от учетной записи
    username, password = console_login()

    client.log.info('Trying to login. User: %s' % username)

    # загружаем фрейм с формой ввода пароля
    client.log.debug('Requesting login frame...')
    response = client.engine.session.get(_get_link(client.log, 'login'))
    client.log.debug('Response: %s Error: %s' % (response.status_code,
                                                 response.reason))

    # находим элемент с id="loginForm" и сохраняем его параметр action
    parser = HTMLAttributeSearch('form', 'id', 'loginForm', 'action')
    parser.feed(response.text)
    login_target = parser.result
    client.log.debug('Login form submit url: %s' % login_target)

    login_data = {
        'className': 'login ',
        'email': username,
        'password': password,
        'remember_me': 0,
    }

    # отправляем логин и пароль на сервер
    client.log.debug('Sending credentials...')
    response = client.engine.session.post(login_target, data=login_data)
    client.log.debug('Response: %s Error: %s' % (response.status_code,
                                                 response.reason))

    # загружаем фрейм с выбором id мира для входа
    client.log.debug('Requesting world selection frame...')
    response = client.engine.session.get(_get_link(client.log,
                                                   'external-avatar-list'))
    client.log.debug('Response: %s Error: %s' % (response.status_code,
                                                 response.reason))

    # ищем элементы класса loginAvatarForm и сохраняем их параметр action
    parser = HTMLAttributeSearch('form', 'class', 'loginAvatarForm', 'action')
    parser.feed(response.text)
    world_target = parser.result
    client.log.debug('World selection form submit url: %s' % world_target)

    # TODO: add 'choose world' feature here.
    world_id = 0
    world_data = {
        'world': world_id,
    }

    # отправляем id мира на сервер
    client.log.info('Entering world %s...' % world_data['world'])
    response = client.engine.session.post(world_target, data=world_data)
    client.log.debug('Response: %s Error: %s' % (response.status_code,
                                                 response.reason))

    # в ответе находим ссылку класса forwardLink и сохраняем href
    parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
    parser.feed(response.text)
    auth_link = parser.result

    rpc_url, webkey = auth_link.split('?key=')
    rpc_url += 'rpc/flash.php'
    client.log.debug('RPC url: %s' % rpc_url)
    client.log.debug('Web key: %s' % webkey)

    # авторизуемся через эту ссылку (получаем куку в сессию)
    client.log.debug('Authorizing via link: %s' % auth_link)
    response = client.engine.session.get(auth_link)
    client.log.debug('Response: %s Error: %s' % (response.status_code,
                                                 response.reason))

    # Устанавливаем нужные для работы параметры
    client.webkey = webkey
    client.engine.rpc_url = rpc_url
    client.engine.session.headers.update({'content-type': 'application/json'})

    # Проверяем, что все ок
    if not client.is_logged_in():
        print('Authentication failed. Will now exit')
        exit(0)


def console_login():
    print("Please enter you credentials.")
    name = input("Enter name (email): ")
    password = getpass.getpass("Password for %s: " % name)
    return name, password


def _get_link(log, action):
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