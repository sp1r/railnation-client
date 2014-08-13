# -*- coding:utf-8 -*-
"""Клиент сервера railnation"""

import hashlib
import json
import requests
import requests.exceptions
import time
import sys

from railnation.core.railnation_globals import log


CLIENT_CHECKSUM = 'ea24d4af2c566004782f750f940615e5'  # hardcoded in flash-app
MAX_RECONNECT = 10


class Client:
    def __init__(self):
        self.rpc_url = ''
        self.webkey = ''
        self.session = requests.Session()

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
        log.debug('Trying: %s %s %s' % (interface, method, params))
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
                log.warning('Connection problems.')
                time.sleep(1)

            except requests.exceptions.Timeout:
                log.warning('No response from server (timeout).')

            # если нет ошибок - возвращаем ответ
            else:
                log.debug('Response: %s Error: %s Content: %s' %
                          (r.status_code, r.reason, r.text))
                return r.json()

        # более чем 10 неудачных попыток соединения считаем критической
        # ошибкой и выходим
        else:
            log.critical('Too much connection errors. Will now exit.')
            sys.exit(1)


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