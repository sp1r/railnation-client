#-*- coding: utf-8 -*-

__author__ = 'sp1r'

from .base import (
    config,
    log
)

from .client import Client

# эта сущность - наша точка доступа к игровым методам
client = Client()

