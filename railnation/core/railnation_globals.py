# -*- coding:utf-8 -*-
"""Сущности, используемые всеми остальными модулями"""

import requests
import logging


# http session with cookies and chocolate
session = requests.Session()
session.headers.update({"User-Agent": 'Mozilla/5.0 (X11; Ubuntu; '
                                      'Linux x86_64; rv:26.0) '
                                      'Gecko/20100101 '
                                      'Firefox/26.0'})


# file log for debug
log = logging.Logger('rail-nation')

_log_format = logging.Formatter(
    fmt='%(levelname)-10s %(asctime)s: %(message)s',
    datefmt='%d.%m %H:%M:%S',
    style='%')
_file_handler = logging.StreamHandler(
    open('/tmp/railnation-debug.log', 'w'))
_file_handler.setFormatter(_log_format)
_file_handler.setLevel(logging.DEBUG)

log.addHandler(_file_handler)


# game client
from railnation.core.railnation_client import Client
client = Client(session, log)