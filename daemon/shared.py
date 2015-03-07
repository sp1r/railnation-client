# -*- coding:utf-8 -*-
"""docstring"""

import os.path
from threading import Lock

from railnationlib.client import Client

BASE_DIR = os.path.join('/', 'opt', 'rail-daemon')
THREADS = {}

client = Client()
avatar = None


class Judge(object):
    def __init__(self):
        self.__money_amount = 0
        self.__money_access_lock = Lock()

        self.__gold_amount = 0
        self.__gold_access_lock = Lock()

        self.__science_amount = 0
        self.__science_access_lock = Lock()

        self.__train_slots_amount = 0
        self.__train_slots_access_lock = Lock()

        self.__rails_amount = 0
        self.__rails_access_lock = Lock()
        
        self.__license_slot_amount = 0
        self.__license_slot_access_lock = Lock()


judge = Judge()