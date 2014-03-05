#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

import time

from module_templates import ListenerModule
from module_templates import ListenerModuleConfig


class FileLoggerConfig(ListenerModuleConfig):
    def __init__(self):
        ListenerModuleConfig.__init__(self)

        self.time_format = "%H:%M:%S"
        self.log_file_name = "arb.log"
        self.log_file_mode = "w"

        # own services:
        self.provided_services.append('log')


class FileLogger(ListenerModule):
    """
    Централизованное управление логами работы ботов.
    Не фуки-хуяки.
    """
    def __init__(self, config):
        assert isinstance(config, ListenerModuleConfig)
        ListenerModule.__init__(self, config)

        self.log_file = open(self.config.log_file_name,
                             self.config.log_file_mode)

    def open_ports(self):
        """
        Определяет обработчики для входящих сообщений.
        """
        #self.listen[161] = self.change_state
        self.listen[self.config.service_ports['log']] = self.write_to_log

    def write_to_log(self, msg):
        assert isinstance(msg, dict)
        assert 'level' in msg.keys()
        assert 'time' in msg.keys()
        assert 'message' in msg.keys()
        log_line = "%s: %s\n" % (time.strftime(self.config.time_format,
                                              msg['time']), msg['message'])
        self.log_file.write(log_line)
        self.log_file.flush()

    def change_state(self, data):
        pass

    def configure(self):
        pass