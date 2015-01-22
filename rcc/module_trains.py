# -*- coding:utf-8 -*-
"""docstring"""

import time
import logging

from raillib.consts import (
    train_names,
    goods,
    city_names,
)
from rcc.module import ModuleBase


REFRESH_PERIOD = 300


class Module(ModuleBase):
    name = 'trains'

    routes_in = (
        ('show', 'train'),
        ('show', 'trains')
    )

    def __init__(self, avatar):
        ModuleBase.__init__(self)

        self.avatar = avatar
        self.range = []
        self.prompt = 'RN(trains)> '

        self.trains = {}
        self.info_birth = 0

    def update(self):
        train_types = {}
        for train in sorted(self.avatar.my_trains):
            type_id = int(round(train.type, -2))
            try:
                train_types[type_id] += 1
            except KeyError:
                train_types[type_id] = 1

            num = train_types[type_id]
            self.trains[train_names['eng'][type_id] + ('%02d' % num)] = train

        self.info_birth = int(time.time())

    def get_trains(self, skip_cache=False):
        if skip_cache:
            self.update()

        elif int(time.time()) - self.info_birth > REFRESH_PERIOD:
            self.update()

        return self.trains

    def enter(self, command):
        logging.debug('Entering module: Trains')
        if len(command) == 1:
            print('argument required: train-name, trains-range or all')
            return None, None

        # elif command[1] == 'mine':
        #     self.range = [self.player]
        #     self.prompt = 'RN(bonus-mine)> '
        #     logging.debug('Bonuses range: %s' % str(self.range))
        #     return self.name, self.prompt

        elif command[1] == 'all':
            self.range = [self.avatar.my_trains]
            self.prompt = 'RN(trains-all)> '
            logging.debug('Trains range: %s' % str(self.range))
            return self.name, self.prompt

    def execute(self, command):
        logging.debug('Executing module: Trains')
        if len(command) == 0:
            return self.name, self.prompt

        elif command[0] == 'exit':
            return None, None

        elif command[0] == 'park':
            self.park(command)
            return self.name, self.prompt

        elif command[0] == 'haul':
            self.haul(command)
            return self.name, self.prompt

    def park(self, command):
        if len(command) < 2:
            return

        if not command[1] in city_names['eng']:
            print('No such town: %s' % command[1])

    def haul(self, command):
        if len(command) < 2:
            return

    def _set_schedule(self, start, end):
        pass