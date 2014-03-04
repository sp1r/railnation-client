#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

from bot import Bot

from Queue import PriorityQueue
import time


class Job:
    def __init__(self, process_time):
        """
        process_time -- момент времени, когда задание будет готово к выполнению.
        """
        self.process_time = process_time

    def __cmp__(self, other):
        return self.process_time > other.process_time


class SchedulingBot(Bot):
    """
    Бот создающий расписание задач.
    И выполняющий их по порядку.
    """
    def __init__(self, name, pipe):
        Bot.__init__(self, name, pipe)
        self.schedule = PriorityQueue()
        self.current = None

    def bot_logic(self):
        if self.schedule.empty():
            self.hold = True
            return

        if self.current is None:
            self.current = self.schedule.get()

        wait_time = self.current.process_time - int(time.time())
        if wait_time <= 0:
            self.process_job(self.current)
            self.current = None
        else:
            self.wait_for_message(wait_time)

    def process_job(self, job):
        raise NotImplementedError