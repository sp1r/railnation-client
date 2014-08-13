# -*- coding:utf-8 -*-
"""загрузка параметров игры"""

import tempfile
import zlib

from railnation.core.railnation_globals import log
from railnation.core.railnation_client import client
from railnation.core.railnation_errors import NotAuthorized

# параметры игры:
self_id = ''
properties = {}
agent = ''
language = ''


def load_game():
    client.session.headers.update({'content-type': 'application/json'})

    global self_id, properties, agent, language

    self_id = str(client.produce('AccountInterface',
                                 'is_logged_in',
                                 [client.webkey])['Body'])
    if self_id == 'False':
        log.critical('Got "False" instead of player ID while loading!')
        raise NotAuthorized('Cannot load game. Not logged in.')

    t = client.produce('PropertiesInterface',
                       'getData',
                       [])['Body']

    properties = t['properties']
    properties['client'] = t['client']

    agent = client.produce('KontagentInterface',
                           'getData',
                           [])['Body']

    language = str(client.produce('AccountInterface',
                                  'getLanguage',
                                  [])['Body'])

    # TODO: расследовать, одинаковый ли id у ассетов на разных серверах
    r = client.session.get('http://s3.railnation.ru/web/assets/ea24d4af2c56'
                           '6004782f750f940615e5/languagedata.ru-RU.zip')

    tf = tempfile.TemporaryFile()
    tf.write(zlib.decompress(r.content))
    tf.seek(0)
    # parse this file
    tf.close()

    r = client.session.get('http://s3.railnation.ru/web/assets/ea24d4af2c56'
                           '6004782f750f940615e5/languagedata.city-Names.zip')

    tf = tempfile.TemporaryFile()
    tf.write(zlib.decompress(r.content))
    tf.seek(0)
    # parse this file too
    tf.close()

