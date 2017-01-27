#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import time
import json
import hashlib
import six

import requests
import requests.exceptions

from railnation.config import (
    CLIENT_CHECKSUM,
    MAX_RECONNECT,
    CONNECTION_TIMEOUT,
)
from railnation.core.errors import RailNationConnectionProblem
from railnation.core.common import log
from railnation.managers.resources import ResourcesManager


session = requests.Session()
session.headers.update({
    'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/36.0.1985.125 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6',
})

json_communication = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}


def _quote(item):
    """
    Explicit quotation and spacing to ensure correct md5 sum calculation.

    :param item: object
    :type item: str or dict or list of bool or int
    :return: accurately quoted and spaced json
    :rtype: str
    """
    if isinstance(item, list):
        return '[' + ','.join([_quote(i) for i in item]) + ']'
    elif isinstance(item, dict):
        return '{' + ','.join([_quote(k) + ':' + _quote(v)
                               for k, v in item.items()]) + '}'
    elif isinstance(item, six.string_types):
        return '"' + item + '"'
    else:
        return str(item).lower()


def _make_hash(item):
    return hashlib.md5(_quote(item).encode("utf-8")).hexdigest()


class ServerCall:
    def __init__(self):
        self.log = log.getChild('ServerCall')
        self.log.debug('Initialization...')
        self.api_url = None

    def init(self, server_url):
        if server_url.startswith('http'):
            self.api_url = '%s/web/rpc/flash.php' % server_url
        else:
            self.api_url = 'http://%s/web/rpc/flash.php' % server_url
        self.log.debug('Base url for calls: %s' % self.api_url)

    def call(self, interface_name, method_name, data):
        """
        Actual server query.

        Construct URL from base_url + url params "interface" & "method".
        And POST data in json format there.

        In case of an error - retry MAX_RECONNECT times before die.

        :type interface_name: str
        :type method_name: str
        :type data: list
        :return: server response as dict object (parsed from json)
        :rtype: dict
        """
        assert self.api_url is not None

        self.log.debug('Requesting: %s %s' % (interface_name, method_name))
        self.log.debug('Params: %s' % data)

        target = {'interface': interface_name,
                  'method': method_name}
        payload = {'ckecksum': CLIENT_CHECKSUM,
                   'client': 1,
                   'hash': _make_hash(data),
                   'parameters': data}

        retry_count = 0
        while retry_count < MAX_RECONNECT:
            retry_count += 1
            try:
                r = session.post(self.api_url,
                                 params=target,
                                 data=json.dumps(payload),
                                 timeout=CONNECTION_TIMEOUT,
                                 headers=json_communication)

                self.log.debug('Code: %s %s' % (r.status_code,
                                                r.reason))

            except requests.exceptions.ConnectionError as err:
                self.log.error('Connection resulted in error: %s' % str(err))
                time.sleep(0.25)

            except requests.exceptions.Timeout as err:
                self.log.error('Connection timeout: %s' % str(err))
                pass

            else:
                return self._process_response(r.json())

        self.log.critical('Too many connection failures (%s)' % retry_count)
        raise RailNationConnectionProblem('Too many connection failures (%s)'
                                          % retry_count)

    def _process_response(self, response):
        self.log.debug('Error code: %s' % response['Errorcode'])
        if response['Errorcode'] != 0:
            self.log.error('Error message: ')  # todo: get example of error message and throw exception

        try:
            resourses = response['Infos']['Resources']
        except KeyError:
            self.log.debug('No resources info in response')
        else:
            manager = ResourcesManager.get_instance()
            manager.update_resources(resourses)

        self.log.debug('Body: %s' % response['Body'])
        return response['Body']


server = ServerCall()

