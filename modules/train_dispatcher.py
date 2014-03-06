# -*- coding: utf-8 -*-
__author__ = 'spir'


from module_templates import ListenerModule
from module_templates import ListenerModuleConfig


class DispatcherConfig(ListenerModuleConfig):
    def __init__(self):
        ListenerModuleConfig.__init__(self)

        # provided services
        self.provided_services.append('trains')

        # required services
        self.required_services.append('query')


class Dispatcher(ListenerModule):
    def __init__(self, config):
        assert isinstance(config, DispatcherConfig)
        ListenerModule.__init__(self, config)

        self.trains = {}
        self.train_requests = {}

    def open_ports(self):
        """
        Определяет обработчики для входящих сообщений.
        """
        self.listen[self.config.service_ports['control']] = self.change_state
        self.listen[self.config.service_ports['trains']] = self.dispatch_trains

    def configure(self):
        # загружаем список поездов и улучшений
        self.require_attr('trains',
                          'query',
                          ('get_my_trains', ),
                          self.set_trains_list)

    def change_state(self, data):
        pass

    def dispatch_trains(self, data):
        if data[0] in 'get_current_list':
            if self.trains is None:
                return []
            else:
                return self.trains.keys()

################################################################################
#   Callbacks

    def set_trains_list(self, data):
        self.trains = {}
        for train in data['Body']:
            self.trains[str(train['ID'])] = {'status': 'free',
                                             'type': train['type'],
                                             'upgrades': []}
            for up in train['upgrades']:
                self.trains[str(train['ID'])]['upgrades'].append(up['id'])