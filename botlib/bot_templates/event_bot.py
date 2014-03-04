#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

from bot import Bot
import time


class EventBot(Bot):
    """
    Этот тип бота следит за каким-то игровым событием и реагирует на них.
    """
    def __init__(self, name, pipe):
        Bot.__init__(self, name, pipe)
        self.probe_interval = 60  # seconds
        self.next_probe = int(time.time()) + self.probe_interval

    def bot_logic(self):
        wait_time = self.next_probe - int(time.time())
        if wait_time <= 0:
            self.probe_event()
            self.next_probe = int(time.time()) + self.probe_interval
        else:
            self.wait_for_message(wait_time)

    def probe_event(self):
        raise NotImplementedError