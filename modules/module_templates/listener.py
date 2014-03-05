# -*- coding: utf-8 -*-
"""
Скелет модуля, который слушает входящие сообщения и реагирует на них. И все.
"""
__author__ = 'spir'

from module import Module
from module import ModuleConfig


class ListenerModuleConfig(ModuleConfig):
    def __init__(self):
        ModuleConfig.__init__(self)


class ListenerModule(Module):
    def __init__(self, config):
        Module.__init__(self, config)

    def bot_logic(self):
        self.wait_for_message()