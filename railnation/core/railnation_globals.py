# -*- coding:utf-8 -*-
"""Сущности, используемые всеми остальными модулями"""

import logging
import sys
import os

# game client
client = None

# game properties
properties = {}

# python 3?
is_py3 = sys.version_info >= (3, 3)

# linux?
is_linux = sys.platform.startswith('linux')

# set path
work_path = os.path.realpath(os.path.dirname(__file__))
pages_path = os.path.realpath(os.path.join(work_path, '..', 'pages'))

# temporary add pages dir to sys.path, we will restore original value
# after all pages are imported
orig_sys_path = sys.path[:]
sys.path.append(pages_path)


# file log for debug
log = logging.Logger('rail-nation')

_log_format = logging.Formatter(
    fmt='%(levelname)-10s %(asctime)s: %(message)s',
    datefmt='%d/%m %H:%M:%S',
    style='%')
_file_handler = logging.StreamHandler(
    open('/tmp/railnation-debug.log', 'w'))
_file_handler.setFormatter(_log_format)
_file_handler.setLevel(logging.DEBUG)

log.addHandler(_file_handler)