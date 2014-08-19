# -*- coding:utf-8 -*-
"""Исключения"""

from railnation.core.railnation_log import log
log.debug('Loading module: Errors')


class ConnectionProblem(Exception):
    pass


class NotAuthenticated(Exception):
    pass


class ChangeHandler(Exception):
    pass


class MenuItemDuplication(Exception):
    pass