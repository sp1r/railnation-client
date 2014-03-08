# -*- coding: utf-8 -*-
"""
    Чтобы не забивать сервер большим количеством запросов. Все обращения к игре
    проходят только через этот модуль.
"""

__author__ = 'spir'

import client
from core.templates import ListenerModule
from core.templates import ListenerModuleConfig


class WebClientConfig(ListenerModuleConfig):
    def __init__(self):
        """
        Default settings.
        """
        ListenerModuleConfig.__init__(self)
        self.webkey = "42cbf556576ddc85a560ff2d7909c020"
        self.url = "http://s6.railnation.ru/web/rpc/flash.php"
        self.cookie_name = "PHPSESSID"
        self.cookie_value = ""
        self.checksum = "3caf8214532b258daf0118304972727e"

        # own services:
        self.provided_services.append('query')


class WebClient(ListenerModule):

    def __init__(self, config):
        assert isinstance(config, ListenerModuleConfig)
        ListenerModule.__init__(self, config)
        cookie = "=".join((self.config.cookie_name, self.config.cookie_value))
        self.game = client.Oracle(client.Engine(self.config.url,
                                                cookie,
                                                self.config.checksum))
        self.user_id = ''

    def open_ports(self):
        """
        Определяет обработчики для входящих сообщений.
        """
        self.listen[self.config.service_ports['control']] = self.change_state
        self.listen[self.config.service_ports['query']] = self.make_call

    def configure(self):
        r = self.game.get_my_id()
        if r['Body']:
            self.user_id = r['Body']
        else:
            raise Exception('Error! User is not logged in.')

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