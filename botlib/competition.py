#!/usr/bin/python
# -*- coding: utf-8 -*-

_author__ = 'spir'

import time
import random

from bot_templates import SchedulingBot


messages = {
    # service messages
    100: '{0:s} Stranger: Schedule created.',
    101: '{0:s} Stranger: I`m fine. Thank you.',
    102: '{0:s} Stranger: Changed state to HOLD.',
    103: '{0:s} Stranger: Changed state to RUN.',
    # report messages
    200: '{0:s} Stranger: {1:s} Collected.',
    201: '{0:s} Stranger: Got a Ticket! Reward: {1:s}',
    202: '{0:s} Stranger: {1:s} Missed.',
    204: '{0:s} Stranger: {1:s} Bank Overflows!',
    205: '{0:s} Stranger: {1:s} Bank no more Overflowed.',
}


class Stranger(SchedulingBot):
    """
    Класс, собирающий бонусы со станций участников ассоциации.
    """
    def __init__(self, name, pipe):
        SchedulingBot.__init__(self, name, pipe)

        self.names = {}
        self.user_id = ''
        self.corp_id = ''
        self.log_time_format = ''
        self.last_ticket = 0
        self.min_delay = 30
        self.max_delay = 60

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

        self.create_schedule()

    def create_schedule(self):
        """
        Создаем начальное расписание обхода станций.
        """
        self.clear_schedule()

        # Creating schedule with this flag set to True process all buildings.
        # When it is False - ready bonuses won`t be added to schedule.
        self.hold = True

        # прежде всего нужно составить список игроков нашей ассоциации
        self.require_attr('names',
                          'game',
                          ('get_user', self.user_id),
                          self.set_names)

        for player_id in self.names.keys():
            self.send_msg('game',
                          ('get_buildings', player_id),
                          True,
                          self.schedule_collecting,
                          player_id, 9, 10, 11)
            time.sleep(1)  # are we like human?

        self.wait_all_replies()

        self.send_log(6, messages[100].format(self.now()))
        self.hold = False

    def process_job(self, job):
        """
        Обработчик заданий
        """
        player_id, building_id = job

        if player_id == self.user_id:
            self.send_msg('game',
                          ('collect_self', building_id),
                          True,
                          self.log_collecting,
                          player_id, building_id)
        else:
            self.send_msg('game',
                          ('collect', player_id, building_id),
                          True,
                          self.log_collecting,
                          player_id, building_id)

################################################################################
#   Служебные функции


################################################################################
#   Дополнительные функции

    def now(self):
        return time.strftime(self.log_time_format)
