# -*- coding: utf-8 -*-
"""
Модуль, собирающий бонусы со станций участников ассоциации.
"""

_author__ = 'spir'

import time
import random
import Queue

from module_templates import SchedulerModule
from module_templates import SchedulerModuleConfig
from module_templates import SchedulerJob


class StrangerConfig(SchedulerModuleConfig):
    def __init__(self):
        SchedulerModuleConfig.__init__(self)

        self.messages = {
            # service messages
            100: 'Stranger: Schedule created.',
            101: 'Stranger: I`m fine. Thank you.',
            102: 'Stranger: Changed state to HOLD.',
            103: 'Stranger: Changed state to RUN.',
            # report messages
            200: 'Stranger: {0:s} Collected.',
            201: 'Stranger: Got a Ticket! Reward: {0:s}',
            202: 'Stranger: {0:s} Missed.',
            204: 'Stranger: {0:s} Bank Overflows!',
            205: 'Stranger: {0:s} Bank no more Overflowed.',
        }

        self.min_delay = 30
        self.max_delay = 60
        self.collect_self = True

        # required services
        self.required_services.append('log')
        self.required_services.append('query')


class Stranger(SchedulerModule):

    def __init__(self, config):
        SchedulerModule.__init__(self, config)

        self.names = {}
        self.user_id = ''
        self.corp_id = ''
        self.last_ticket = 0

    def configure(self):
        # выясним свой ID
        self.require_attr('user_id',
                          'query',
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
                          'query',
                          ('get_user', self.user_id),
                          self.set_names)

        # теперь запланируем визиты к ним на станцию
        for player_id in self.names.keys():
            self.send_request('query',
                              ('get_buildings', player_id),
                              True,
                              self.schedule_collecting,
                              player_id, 9, 10, 11)
            time.sleep(1)  # human-style?

        self.wait_all_replies()

        self.send_request('log',
                          {'level': 6,
                           'message': self.config.messages[100],
                           'time': time.localtime()})

    def process_job(self, job):
        """
        Обработчик заданий
        """
        if job.player_id == self.user_id:
            self.send_request('query',
                              ('collect_self', job.building_id),
                              True,
                              self.log_collecting,
                              job.player_id, job.building_id)
        else:
            self.send_request('query',
                              ('collect', job.player_id, job.building_id),
                              True,
                              self.log_collecting,
                              job.player_id, job.building_id)

    def change_state(self, data):
        print data

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
                random.randint(self.config.min_delay, self.config.max_delay)
            job = CollectingJob(collect_at, player_id, building_id)
            self.schedule.put(job)

################################################################################
#   Callbacks
#
#   Эти функции проводят разбор ответов от других ботов.
#   Формат сообщений описан в соответствующих классах.

    def set_own_id(self, data):
        self.user_id = str(data['Body'])

    def set_names(self, data):
        data = data['Body']
        if "corporation" in data.keys():
            self.corp_id = str(data['corporation']['ID'])
            self.send_request('query',
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
            self.send_request('log',
                              {'level': 6,
                              'message': self.config.messages[204].format(
                                  self.names[player_id]),
                              'time': time.localtime()})
            # will check again after an hour
            collect_at = int(time.time()) + 3600
            job = CollectingJob(collect_at, player_id, building_id)
            self.schedule.put(job)

        elif not data["Body"]:
            # already collected by someone
            # or user deleted from corp
            self.send_request('log',
                              {'level': 6,
                              'message': self.config.messages[202].format(
                                  self.names[player_id]),
                              'time': time.localtime()})
            self.send_request('query',
                              ('get_buildings', player_id),
                              True,
                              self.schedule_collecting,
                              player_id, building_id)

        else:
            # collected
            self.send_request('log',
                              {'level': 6,
                              'message': self.config.messages[200].format(
                                  self.names[player_id]),
                              'time': time.localtime()})
            self.send_request('query',
                              ('check_lottery',),
                              True,
                              self.check_ticket,
                              self.message_number)
            self.send_request('query',
                              ('get_buildings', player_id),
                              True,
                              self.schedule_collecting,
                              player_id, building_id)

    def check_ticket(self, data, message_number):
        if data['Body']['freeSlot'] and self.last_ticket < message_number:
            self.last_ticket = self.message_number + 1
            self.send_request('query',
                              ('collect_ticket',),
                              True,
                              self.log_ticket)

    def log_ticket(self, data):
        self.send_request('log',
                          {'level': 6,
                          'message': self.config.messages[201].format(
                              str(data['Infos'])),
                          'time': time.localtime()})


class CollectingJob(SchedulerJob):
    def __init__(self, ready_at, player_id, building_id):
        SchedulerJob.__init__(self, ready_at)
        self.player_id = player_id
        self.building_id = building_id