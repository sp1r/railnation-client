#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

from bot_templates import ListenerBot


class Chronicler(ListenerBot):
    """
    Централизованное управление логами работы ботов.
    Не фуки-хуяки.

    Сервисы:
       Порт 514.
          На входе ожидаются следующие сообщения:
          msg = {'level':XX, 'message':TEXT}
          Сообщение будет записано в лог. Ответ не посылается.
       Порт 80.
          Сообщение может быть любым.
          Будет возвращена строка, содержащая текущий формат времени в логах.
    """
    def __init__(self, name, pipe):
        ListenerBot.__init__(self, name, pipe)
        self.time_format = "%H:%M:%S"
        self.log_file = open('main.log', 'a+')

    def configure(self):
        self.listen[514] = self.write_to_log
        self.listen[80] = self.send_current_format

    def write_to_log(self, log_msg):
        assert isinstance(log_msg, dict)
        assert 'level' in log_msg.keys()
        assert 'message' in log_msg.keys()
        self.log_file.write(log_msg['message'])
        self.log_file.write('\n')
        self.log_file.flush()

    def send_current_format(self, data):
        return self.time_format

    def change_state(self, data):
        pass