# -*- coding:utf-8 -*-
"""docstring"""


import modules.template
import daemon.shared


class Module(modules.template.ModuleBase):
    name = 'build'
    api = {}

    def set_attributes(self):
        self.build_queue = []

    def upgrade(self, building_id):
        self.build_queue.append(building_id)

    def clear(self):
        self.build_queue = []

    def work(self):
        pass