#-*- coding: utf-8 -*-
"""
Модуль аутентификации на игровом сервере.

Перед началом работы необходимо вызвать один из пользовательских функций,
которые получают имя пользователя и пароль из какого-либо источника и
запускают сценарий аутентификации.

На данный момент реализованы функции:
quick_login - значения забиты в функцию
console_login - запрашивает ввод значений с консоли
"""

__author__ = 'sp1r'

import html.parser

from . import log
from . import config
from . import session


log.info('Authorization module Initialization...')


###############################################################################
# Загрузка конфигурации SAM
sam_url = 'http://' + config['base_url'] + '/js/sam.config.php'
config['sam'] = {}

log.debug('Downloading SAM config...')
log.debug('SAM config url: %s' % sam_url)
response = session.get(sam_url)
log.debug('Response: %s Error: %s' % (response.status_code,
                                      response.error))

# парсим строки вида:
# samConfig['applicationId'] = 'railnation';
for line in response.iter_lines():
    # iter_lines() возвращает объекты типа <bytes> - нужно конвертировать
    line = str(line)
    if line.startswith('b"samConfig['):
        fields = line.split("'")
        key, value = fields[1], fields[3]
        config['sam'][key] = value
        log.debug('SAM item: %s = %s' % (key, config['sam'][key]))


###############################################################################
# Конструктор ссылок
def _get_link(action):
    """
    Повторяет функционал из http://www.rail-nation.com/js/sam.js
    """
    log.debug('Constructing url for %s frame' % action)
    target = "%s/iframe/%s/applicationId/%s/applicationCountryId/%s" \
             "/applicationInstanceId/%s/userParam/undefined/" % \
             (config['sam']['url'],
              action,
              config['sam']['applicationId'],
              config['sam']['applicationCountryId'],
              config['sam']['applicationInstanceId'])
    log.debug('Link for %s frame is: %s' % (action, target))
    return target


###############################################################################
# Сценарий входа в игру.
def _authorize(username, password, world):
    """
    Проводит аутентификацию.

    :param username: email (имя пользователя)
    :param password: пароль
    :param world: id игрового мира
    :return: None
    """
    log.info('Trying to login. User: %s' % username)

    # загружаем фрейм с формой ввода пароля
    log.debug('Requesting login frame...')
    response = session.get(_get_link('login'))
    log.debug('Response: %s Error: %s' % (response.status_code,
                                          response.error))

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
    response = session.post(login_target, data=login_data)
    log.debug('Response: %s Error: %s' % (response.status_code,
                                          response.error))

    # загружаем фрейм с выбором id мира для входа
    log.debug('Requesting world selection frame...')
    response = session.get(_get_link('external-avatar-list'))
    log.debug('Response: %s Error: %s' % (response.status_code,
                                          response.error))

    # ищем элементы класса loginAvatarForm и сохраняем их параметр action
    parser = HTMLAttributeSearch('form', 'class', 'loginAvatarForm', 'action')
    parser.feed(response.text)
    world_target = parser.result
    log.debug('World selection form submit url: %s' % world_target)

    # TODO: add 'choose world' feature here.

    world_data = {
        'world': world,
    }

    # отправляем id мира на сервер
    log.info('Entering world %s...' % world_data['world'])
    response = session.post(world_target, data=world_data)
    log.debug('Response: %s Error: %s' % (response.status_code,
                                          response.error))

    # в ответе находим ссылку класса forwardLink и сохраняем href
    parser = HTMLAttributeSearch('a', 'class', 'forwardLink', 'href')
    parser.feed(response.text)
    auth_link = parser.result

    config['rpc_url'], config['web_key'] = auth_link.split('/web/?key=')
    config['rpc_url'] += '/web/rpc/flash.php'
    log.debug('RPC url: %s' % config['rpc_url'])
    log.debug('Web key: %s' % config['web_key'])

    # авторизуемся через эту ссылку (получаем куку в сессию)
    log.debug('Authorizing via link: %s' % auth_link)
    response = session.get(auth_link)
    log.debug('Response: %s Error: %s' % (response.status_code,
                                          response.error))


###############################################################################
# Пользовательские методы входа в игру
def quick_login():
    name = '***'
    password = '***'
    world = 354
    _authorize(name, password, world)


def console_login():
    print("Now you`ll login through console input")
    name = input("Enter name: ")
    password = input("Password for %s: " % name)
    world = input("World id to enter:")
    _authorize(name, password, world)


###############################################################################
# Парсеры html
class HTMLAttributeSearch(html.parser.HTMLParser):
    def __init__(self, tag_to_find,
                 filter_attr, filter_attr_value, target_attr):
        html.parser.HTMLParser.__init__(self)
        self.interesting_tag = tag_to_find
        self.filter = filter_attr
        self.filter_value = filter_attr_value
        self.target = target_attr
        self.result = None

    def handle_starttag(self, tag, attrs):
        if tag == self.interesting_tag:
            attributes = {k: v for k, v in attrs}
            if self.filter in attributes and \
                    attributes[self.filter] == self.filter_value:
                self.result = attributes[self.target]


###############################################################################
# Секция тестирования
if __name__ == "__main__":
    response = session.get(_get_link('login'))
    doc = HTMLAttributeSearch('form', 'id', 'loginForm', 'action')
    doc.feed(response.text)
    print(doc.result)