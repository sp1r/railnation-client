#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

import Queue

from core.templates import ListenerBot


class Scientist(ListenerBot):
    """
    Бот, занимающийся исследованиями.
    """
    def __init__(self, name, pipe):
        ListenerBot.__init__(self, name, pipe)
        self.time_format = "%H:%M:%S"
        self.research_queue = Queue.Queue()
        self.current = 0

    def prepare(self):
        # self.research_queue.put(240602)
        # self.research_queue.put(240605)
        # self.research_queue.put(240001)
        self.current = self.research_queue.get()
        self.send_msg('judge', (4, 1), True, self.research_next)

    def process_message(self, source, label, msg):
        pass

    def research_next(self, data):
        assert data == 'continue'
        self.send_msg('game',
                      ('research', self.current, 1),
                      True,
                      self.update_queue)

    def update_queue(self, data):
        if data['Body']:
            self.current = self.research_queue.get()
        self.send_msg('judge', (4, 1), True, self.research_next)