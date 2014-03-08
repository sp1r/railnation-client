#!/usr/bin/python
# -*- coding: utf-8 -*-

_author__ = 'spir'

import time

from core.templates import EventBot


messages = {
    # service messages
    101: '{0:s} Mechanic: I`m fine. Thank you.',
    102: '{0:s} Mechanic: Changed state to HOLD.',
    103: '{0:s} Mechanic: Changed state to RUN.',
    # report messages
    200: '{0:s} Mechanic: Train {1:s} needs repairing. Reliability: {2:f}',
    201: '{0:s} Mechanic: Train {1:s} repaired',
}


class Mechanic(EventBot):
    """
    Класс, поезда починяющий
    """
    def __init__(self, name, pipe):
        EventBot.__init__(self, name, pipe)

        self.user_id = ''
        self.trains = []
        self.repair_needed = []
        self.log_time_format = ''
        self.repair_floor = 85.0
        self.refresh_interval = 60  # seconds

    def prepare(self):
        # выясним текущий формат ведения лога
        self.require_attr('log_time_format',
                          'log',
                          {'request_code': 100},
                          self.set_time_format)

        # и свой ID
        self.require_attr('user_id',
                          'game',
                          ('get_my_id',),
                          self.set_own_id)

        # и запросим список поездов
        self.require_attr('trains',
                          'game',
                          ('get_my_trains',),
                          self.set_trains)

    def probe_event(self):
        self.repair_needed = []
        for train_id in self.trains:
            self.send_msg('game',
                          ('get_train', train_id),
                          True,
                          self.check_train,
                          train_id)
            time.sleep(1)  # are we like human?

        self.wait_all_replies()

        if self.repair_needed:
            self.send_msg('game',
                          ('get_my_trains', ),
                          True,
                          self.do_maintenance)
        self.wait_all_replies()

################################################################################
#   Callbacks
#
#   Эти функции проводят разбор ответов от других ботов.
#   Формат сообщений описан в соответствующих классах.

    def set_time_format(self, data):
        self.log_time_format = data

    def set_own_id(self, data):
        self.user_id = str(data['Body'])

    def set_trains(self, data):
        self.trains = []
        for train in data['Body']:
            self.trains.append(str(train['ID']))

    def check_train(self, data, train_id):
        if data['Body']['reliability'] < self.repair_floor:
            self.repair_needed.append(train_id)
            self.send_log(6, messages[200].format(self.now(),
                                                  train_id,
                                                  data['Body']['reliability']))

    def do_maintenance(self, data):
        for train in data['Body']:
            if str(train['ID']) in self.repair_needed:
                self.send_msg('judge',
                              (1, train['maintenance_costs']),
                              True,
                              self.repair_train,
                              str(train['ID']))

    def repair_train(self, data, train_id):
        assert data == 'continue'
        self.send_msg('game', ('repair_train', train_id))
        self.send_log(6, messages[201].format(self.now(),
                                              train_id))

################################################################################
#   Дополнительные функции

    def now(self):
        return time.strftime(self.log_time_format)

    def process_message(self, msg_from, msg_num, data):
        pass