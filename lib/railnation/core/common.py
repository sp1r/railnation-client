#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
Common module parameters like directories and suffixes.
Not configurable.
"""

import os
import logging

# Try to guess where we are
base_dir = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    os.path.pardir,
    os.path.pardir
))

html_dir = os.path.join(base_dir, 'html')
lib_dir = os.path.join(base_dir, 'lib')


log = logging.getLogger('RailNation')
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s: %(levelname)8s: %(name)s: %(message)s',
                                           datefmt='%Y-%d-%m %H:%M:%S'))
log.addHandler(log_handler)