__author__ = 'spir'

import time

from core.templates import EventModule
from core.templates import EventModuleConfig


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

        self.kostil = {
            0: "318d7429-1c80-4e10-b93d-abca948def4b",
            1: "0dc52a2a-10c3-451f-bd84-378e67a6e5d6",
            2: "0e03e417-7601-48e1-88d9-c90276d003b3",
            4: "8fca71ab-9194-4230-9875-a0d33703a126",
            5: "2ec99a68-ea46-435b-af95-ad80893fcf60",
        }


class Logistics(EventModule):
    def __init__(self, config):
        assert isinstance(config, LogisticsConfig)
        EventModule.__init__(self, config)

        self.trains = []
        self.roadmaps = {}

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

    def change_state(self, data):
        new_target = int(data[0])

        new_roadmap = [
            {'dest_id': self.config.kostil[new_target],
            'loading': [{'load': 3, 'type': new_target, 'unload': 0}],
            'scheduleType': 1,
            'wait': 60},
            {'dest_id': self.config.kostil[0],
            'loading': [{'load': 0, 'type': new_target, 'unload': 3}],
            'scheduleType': 1,
            'wait': 0}
             ]

        for train_id in self.trains:
            self.send_request('query',
                              ('get_train_road_map', train_id),
                              True,
                              self.get_roadmap,
                              train_id)

        self.wait_all_replies()

        for train_id in self.trains:
            self.send_request('query',
                              ('get_train', train_id),
                              True,
                              self.set_new_roadmap,
                              train_id, new_roadmap)

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

    def get_roadmap(self, data, train_id):
        self.roadmaps[train_id] = data['Body']

    def set_new_roadmap(self, data, train_id, road):
        if data['Body']['current_location_id'] == self.config.kostil[0]:
            next_loc = str(data['Body']['next_visible_location_id'])
            final_roadmap = [
                {'dest_id': next_loc,
                'loading': [],
                'scheduleType': 2,
                'wait': -1},
                {'dest_id': self.config.kostil[0],
                'loading': [],
                'scheduleType': 2,
                'wait': -1}
            ]
            final_roadmap.extend(road)
            self.send_request('query',
                              ('set_road_map', train_id, final_roadmap),
                              True,
                              self.get_results)

    def get_results(self, data):
        print data