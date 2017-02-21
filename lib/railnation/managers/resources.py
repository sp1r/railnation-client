#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import json

from railnation.core.common import log


class ResourcesManager:
    """
    Resources container.
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: ResourcesManager
        """
        if ResourcesManager.instance is None:
            ResourcesManager.instance = ResourcesManager()

        return ResourcesManager.instance

    def __init__(self):
        self.log = log.getChild('ResourcesManager')
        self.log.debug('Initializing...')

        self.resources = {}
        self.limits = {}

    def update_resources(self, resources):
        try:
            j = json.loads(resources)
        except ValueError:
            self.log.error('Cannot parse resources: %s' % resources)
        else:
            self.resources = {i: 0 for i in range(13)}
            self.resources.update({i: 0 for i in range(61, 75)})
            self.resources.update({int(k): int(v) for k, v in j.items()})

    def update_resource(self, resource_id, amount):
        self.resources[resource_id] = amount if self.limits >= 0 and amount < self.limits[resource_id] else self.limits[resource_id]

    @property
    def free_tickets_count(self):
        try:
            return self.resources[9]
        except KeyError:
            return 0

    @property
    def science_points(self):
        try:
            return self.resources[3]
        except KeyError:
            return 0

    def have_enough_money(self, amount):
        return self.resources[0] >= amount
