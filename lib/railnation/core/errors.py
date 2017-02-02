#!/usr/bin/env python
# -*- coding:  utf-8 -*-


class RailNationClientError(Exception):
    pass


class RailNationNotAuthenticated(RailNationClientError):
    pass


class RailNationInitializationError(RailNationClientError):
    pass


class RailNationConnectionProblem(RailNationClientError):
    pass


class RailNationDoubleLogin(RailNationClientError):
    pass

