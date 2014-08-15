# -*- coding:utf-8 -*-
"""Исключения"""


class ConnectionProblem(Exception):
    pass


class NotAuthorized(Exception):
    pass


class ChangePage(Exception):
    pass