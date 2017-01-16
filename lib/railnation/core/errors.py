#!/usr/bin/env python
# -*- coding:  utf-8 -*-


class RailNationClientError(Exception):
    pass


class RailNationInitializationError(RailNationClientError):
    pass


class RailNationConnectionProblem(RailNationClientError):
    pass

