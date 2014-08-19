# -*- coding:utf-8 -*-
"""Logging for the whole application"""

import logging

# file log for debug
log = logging.Logger('rail-nation')

_log_format = logging.Formatter(
    fmt='%(levelname)-10s %(asctime)s: %(message)s',
    datefmt='%d/%m %H:%M:%S',
    style='%')
_file_handler = logging.StreamHandler(open('/tmp/railnation-debug.log', 'w'))
_file_handler.setFormatter(_log_format)
_file_handler.setLevel(logging.DEBUG)

log.addHandler(_file_handler)
log.info('===================================================================')
log.info('                         New run!                                  ')
log.info('===================================================================')