#!/usr/bin/env python
# -*- coding:  utf-8 -*-

from railnation.core.common import log
from railnation.core.server import server


class AssociationManager:
    """
    Association info and management.
    """

    instances = {}

    @staticmethod
    def get_instance(association_id):
        """
        :rtype: AssociationManager
        """
        try:
            return AssociationManager.instances[association_id]
        except KeyError:
            AssociationManager.instances[association_id] = AssociationManager(association_id)
            return AssociationManager.instances[association_id]

    def __init__(self, association_id):
        self.log = log.getChild('AssociationManager')
        self.log.debug('Initializing association: %s' % association_id)
        self.id = association_id
        self.rank = None
        self.name = ''
        self.prestige = 0
        self.members = []
        self.chair = None
        self.deputies = []

        self.update()

    def update(self):
        self.rank = server.call('CorporationHighscoreInterface', 'getRank', [self.id])
        self.log.debug('Corporation rank: %s' % self.rank)

        #r = server.call('CorporationHighscoreInterface', 'get', [35, 40])

        #r = server.call('CorporationInterface', 'getVCard', [[uuid]])

        r = server.call('CorporationInterface', 'get', [self.id])

        self.name = r['name']
        self.prestige = int(float(r['prestige']))
        for member in r['member']:
            self.members.append(member['user_id'])
            if int(member['title']) == 0:
                self.chair = member['user_id']
            elif int(member['title']) == 1:
                self.deputies.append(member['user_id'])
