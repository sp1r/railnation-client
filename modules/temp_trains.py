# -*- coding:utf-8 -*-
"""docstring"""

import time
import logging

from railnationlib.consts import (
    train_names,
    goods,
    city_names,
    city_ids,
)
from rcc.module import ModuleBase
from railnationlib.models import Schedule

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
            self.range = self.avatar.my_trains
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

        if not command[1] in city_names['eng'].values():
            print('No such town: %s' % command[1])
            return

        logging.info('Parking %d trains to %s' % (len(self.range), command[1]))

        for city_num, name in city_names['eng'].items():
            if command[1] == name.capitalize():
                end_point = city_ids[city_num]

        logging.debug('Found city id: %s' % end_point)

        for train in self.range:
            logging.debug('Parking train: %s' % train.id)
            train.update_navigation()

            logging.debug('Searching route from: %s to: %s' % (
                train.navigation['next_location_id'],
                end_point)
            )
            path = self.avatar.map.get_route(
                train.navigation['next_location_id'],
                end_point
            )
            if path is None:
                logging.info('Town %s is not connected. '
                             'Cannot park there.' % command[1])

            logging.debug('Route length: %s' % path.qsize())

            schedule = Schedule()
            while not path.empty():
                next_location = path.get()
                logging.debug('Route element: Pass by %s' % next_location)
                schedule.append_temporary(next_location)
            train.set_schedule(schedule)

    def haul(self, command):
        if len(command) < 2:
            return