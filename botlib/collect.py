#!/usr/bin/python
# -*- coding: utf-8 -*-

_author__ = 'spir'

import time
import random
import Queue

from bot_templates import SchedulingBot
from bot_templates import Job

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

    def configure(self):
        # выясним текущий формат ведения лога
        self.require_attr('log_time_format',
                          'log', 80,
                          (),
                          self.set_time_format)

        # и свой ID
        self.require_attr('user_id',
                          'game', 530,
                          ('get_my_id',),
                          self.set_own_id)

        self.create_schedule()

    def create_schedule(self):
        """
        Создаем начальное расписание обхода станций.
        """
        self.schedule = Queue.PriorityQueue()

        # прежде всего нужно составить список игроков нашей ассоциации
        self.require_attr('names',
                          'game', 530,
                          ('get_user', self.user_id),
                          self.set_names)

        # теперь запланируем визиты к ним на станцию
        for player_id in self.names.keys():
            self.send_msg('game', 530,
                          ('get_buildings', player_id),
                          True,
                          self.schedule_collecting,
                          player_id, 9, 10, 11)
            time.sleep(1)  # human-style

        self.wait_all_replies()

        self.send_log(6, messages[100].format(self.now()))

    def process_job(self, job):
        """
        Обработчик заданий
        """
        if job.player_id == self.user_id:
            self.send_msg('game', 530,
                          ('collect_self', job.building_id),
                          True,
                          self.log_collecting,
                          job.player_id, job.building_id)
        else:
            self.send_msg('game', 530,
                          ('collect', job.player_id, job.building_id),
                          True,
                          self.log_collecting,
                          job.player_id, job.building_id)

    def change_state(self, data):
        pass

################################################################################
#   Служебные функции

    def schedule_collecting(self, data, player_id, *buildings):
        """
        Добавляет в расписание задания по сбору бонуса со станции.

        Аргументы:
           data -- (dict) информация о станции игрока
           player_id -- (string) владелец станции
           buildings -- (tuple) список зданий, которые нужно поместить
                        в расписание
        """
        data = data["Body"]
        for building_id in buildings:
            ready_after = int(data[str(building_id)]["productionTime"])
            collect_at = int(time.time()) + ready_after + \
                random.randint(self.min_delay, self.max_delay)
            job = _CollectingJob(collect_at, player_id, building_id)
            self.schedule.put(job)

################################################################################
#   Callbacks
#
#   Эти функции проводят разбор ответов от других ботов.
#   Формат сообщений описан в соответствующих классах.

    def set_time_format(self, data):
        self.log_time_format = data

    def set_own_id(self, data):
        self.user_id = str(data['Body'])

    def set_names(self, data):
        data = data['Body']
        if "corporation" in data.keys():
            self.corp_id = str(data['corporation']['ID'])
            self.send_msg('game', 530,
                          ('get_corp', self.corp_id),
                          True,
                          self.parse_corp)
        else:
            self.corp_id = 'none'
            self.names = {data['user_id']: data['username'].encode('utf-8')}

    def parse_corp(self, data):
        self.names = {}
        for member in data['Body']["members"]:
            if member["title"] == '3':
                continue
            self.names[str(member["user_id"])] = member["name"].encode('utf-8')

    def log_collecting(self, data, player_id, building_id):
        if data["Errorcode"] == 10054:
            # bank overflow
            self.send_log(6, messages[204].format(self.now(),
                                                  self.names[player_id]))
            # will check again after an hour
            collect_at = int(time.time()) + 3600
            job = (collect_at, player_id, building_id)
            self.schedule.put(job)

        elif not data["Body"]:
            # already collected by someone
            # or user deleted from corp
            self.send_log(6, messages[202].format(self.now(),
                                                  self.names[player_id]))
            self.send_msg('game',
                          ('get_buildings', player_id),
                          True,
                          self.schedule_collecting,
                          player_id, building_id)

        else:
            # collected
            self.send_log(6, messages[200].format(self.now(),
                                                  self.names[player_id]))
            self.send_msg('game',
                          ('check_lottery',),
                          True,
                          self.check_ticket,
                          self.message_number)
            self.send_msg('game',
                          ('get_buildings', player_id),
                          True,
                          self.schedule_collecting,
                          player_id, building_id)

    def check_ticket(self, data, message_number):
        if data['Body']['freeSlot'] and self.last_ticket < message_number:
            self.last_ticket = self.message_number + 1
            self.send_msg('game',
                          ('collect_ticket',),
                          True,
                          self.log_ticket)

    def log_ticket(self, data):
        self.send_log(6, messages[201].format(self.now(),
                                              str(data['Infos'])))


class _CollectingJob(Job):
    def __init__(self, ready_at, player_id, building_id):
        Job.__init__(self, ready_at)
        self.player_id = player_id
        self.building_id = building_id