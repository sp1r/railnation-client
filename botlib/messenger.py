#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

import raillib
from bot_templates import ListenerBot


class Messenger(ListenerBot):
    """
    Чтобы не забивать сервер большим количеством запросов. Все обращения к игре
    проходят только через этот класс.

    Сервисы:
       Порт 530.
          На входе ожидаются сообщения вида:
          msg = (method_name, *params)
          Ответ - dict, который будет получен от сервера.
    """
    def __init__(self, name, pipe, conn):
        ListenerBot.__init__(self, name, pipe)
        self.game = raillib.Oracle(raillib.Engine(conn))
        self.user_id = ''

    def configure(self):
        self.listen[530] = self.make_call

        r = self.game.get_my_id()
        if r['Body']:
            self.user_id = r['Body']
        else:
            raise Exception('Sorry. User is not logged in.')

    def make_call(self, data):
        if data[0] == 'get_my_id':
            return {'Body': self.user_id}
        assert hasattr(self.game, data[0]), \
            " ".join(('Unknown function to call:', data[0]))
        call = getattr(self.game, data[0])
        if len(data) > 1:
            return call(*data[1:])
        else:
            return call()

    def change_state(self, data):
        pass