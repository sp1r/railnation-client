__author__ = 'spir'

import time

from module_templates import EventModule
from module_templates import EventModuleConfig


class LogisticsConfig(EventModuleConfig):
    def __init__(self):
        EventModuleConfig.__init__(self)

        self.probe_interval = 300  # seconds
        self.policy = ('heavy-supply',
                       '318d7429-1c80-4e10-b93d-abca948def4b',
                       2)

        # required services
        self.required_services.append('trains')
        self.required_services.append('query')


class Logistics(EventModule):
    def __init__(self, config):
        assert isinstance(config, LogisticsConfig)
        EventModule.__init__(self, config)

        self.trains = []

    def configure(self):
        self.require_attr('trains',
                          'trains',
                          ('get_current_list',),
                          self.set_trains)

    def probe_event(self):
        for train_id in self.trains:
            self.send_request('query',
                              ('get_train_road_map', train_id),
                              True,
                              self.check_politics)

################################################################################
#   Callbacks

    def set_trains(self, data):
        if len(data) == 0:
            time.sleep(2)
            self.send_request('trains',
                              ('get_current_list',),
                              True,
                              self.set_trains)
        else:
            self.trains = data

    def check_politics(self, data):
        action, target, good = self.config.policy
        print 'analysing...'
        if action == 'heavy-supply':
            start = data['Body'][0]
            print start['loading'][0]['type'], good
            if start['loading'][0]['type'] != good:
                print 'policy incorrect!'
                return