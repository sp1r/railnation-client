# -*- coding:utf-8 -*-
"""
Entities to be used over the whole application
"""

import sys
import os

################################################################################
# python 3?
is_py3 = sys.version_info >= (3, 3)

# linux?
is_linux = sys.platform.startswith('linux')

# set path
work_path = os.path.realpath(os.path.dirname(__file__))
handlers_path = os.path.realpath(os.path.join(work_path, '..', 'handlers'))

# temporary add pages dir to sys.path, we will restore original value
# after all pages are imported
orig_sys_path = sys.path[:]
sys.path.append(handlers_path)