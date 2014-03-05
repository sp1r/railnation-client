#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

from Queue import PriorityQueue

from module_templates import EventBot


class Judge(EventBot):
    """
    Класс занимающийся распределением ресурсов между другими ботами.

    Сервисы:
       Порт 88.
          На входе ожидаются сообщения вида:
          msg = (reply_name, reply_number, resource_type, amount)
          Ответ - 'continue', когда ресурсы выделены
    """
    def __init__(self, name, pipe):
        EventBot.__init__(self, name, pipe)
        self.refresh_interval = 300  # seconds
        self.priority = {
            'repair': 200,
            'research': 500,
        }
        self.resources = {}
        self.demands = {
            1: PriorityQueue(),
            2: PriorityQueue(),
            4: PriorityQueue(),
        }

    def configure(self):
        self.listen[88] = self.accept_request

    def probe_event(self):
        self.require_attr('resources',
                          'game', 530,
                          ('get_gui', ),
                          self.set_resources)

        for res_type in self.demands.keys():
            while not self.demands[res_type].empty():
                demand = self.demands[res_type].get()
                if demand.amount <= self.resources[res_type]:
                    self.resources[res_type] -= demand.amount
                    self.send_msg(demand.bot_name,
                                  demand.reply_number,
                                  'continue')
                else:
                    self.demands[res_type].put(demand)
                    break

    def accept_request(self, data):
        reply_name, reply_number, resource_type, amount = data
        assert resource_type in self.demands.keys(), \
            " ".join(('Unknown resource type', resource_type))
        d = _Demand(reply_name, reply_number, amount, self.priority[reply_name])
        self.demands[resource_type].put(d)

    def set_resources(self, data):
        self.resources = {}
        data = data['Body']['resources']
        self.resources[1] = int(data['1']['amount'])
        self.resources[2] = int(data['2']['amount'])
        self.resources[4] = int(data['4']['amount'])

    def change_state(self, data):
        pass


class _Demand:
    def __init__(self, name, label, amount, priority):
        self.bot_name = name
        self.reply_number = label
        self.amount = amount
        self.priority = priority

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)