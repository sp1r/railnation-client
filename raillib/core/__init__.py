#-*- coding: utf-8 -*-
"""
Сущности, обеспечивающие работу всей системы в целом.
"""
__author__ = 'sp1r'

import logging
import sys
import requests

# Конфигурация
# TODO: добавить возможность чтения конфигурации из файла
config = {
    'base_url': 'www.rail-nation.com',
    'checksum': 'ea24d4af2c566004782f750f940615e5',
    'lang': 'rus',
}

# Логирование
# TODO: добавить возможность чтения конфигурации логирования из файла
log = logging.Logger('rail-nation')

log_format = logging.Formatter(fmt='%(levelname)-10s %(asctime)s: %(message)s',
                               datefmt='%d.%m %H:%M:%S',
                               style='%')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

file_handler = logging.StreamHandler(open('/tmp/rails-debug.log', 'w'))
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.DEBUG)

log.addHandler(console_handler)
log.addHandler(file_handler)

# Сессия
# в нее будут устанавливаться куки при авторизации
session = requests.Session()
session.headers.update({"User-Agent":
                        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) '
                        'Gecko/20100101 Firefox/26.0'})

###############################################################################
# Start working
log.info('System started.')

from .client import Client

# Эта сущность - точка доступа к игровой информации, которую мы предоставляем
# наверх.
client = Client()