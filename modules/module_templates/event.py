
# -*- coding: utf-8 -*-
"""
Скелет модуля, который следит за каким-то игровым событием и реагирует на него.
"""
__author__ = 'spir'

from module import Module
from module import ModuleConfig
import time


class EventModuleConfig(ModuleConfig):
    def __init__(self):
        ModuleConfig.__init__(self)
        self.probe_interval = 60  # seconds


class EventModule(Module):
    def __init__(self, config):
        assert isinstance(config, EventModuleConfig)
        Module.__init__(self, config)
        self.next_probe = int(time.time()) + self.config.probe_interval

    def bot_logic(self):
        wait_time = self.next_probe - int(time.time())
        if wait_time <= 0:
            self.probe_event()
            self.next_probe = int(time.time()) + self.config.probe_interval
        else:
            self.wait_for_message(wait_time)

    def probe_event(self):
        raise NotImplementedError