#-*- coding: utf-8 -*-
"""
Микро-модуль содержащий "глобальные" сущности настроек и логирования.

Для доступа к настройкам из любой другой части команды будет достаточно написать:
from core.base import config

Более того, изменения, сделанные в этой сущности, будут видны все остальным частям.

TODO: Добавить возможность конфигурирования.
"""

__author__ = 'sp1r'

import logging
import sys

# this instance is our config
config = {
    'base_url': 'www.rail-nation.com',
    'checksum': 'ea24d4af2c566004782f750f940615e5',
}

# this instance is our logger
log = logging.Logger('rail-nation')

log_format = logging.Formatter('%(levelname)-6s %(asctime)s %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

file_handler = logging.StreamHandler(open('/tmp/rails-debug.log', 'w'))
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.DEBUG)

log.addHandler(console_handler)
log.addHandler(file_handler)
