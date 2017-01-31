#!/usr/bin/env python
# -*- coding:  utf-8 -*-

from railnation.core.common import log
from railnation.core.server import server

from railnation.managers.avatar import AvatarManager


class AssociationManager:
    """
    Association info and management.
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: AssociationManager
        """
        if AssociationManager.instance is None:
            AssociationManager.instance = AssociationManager()
        return AssociationManager.instance

    def __init__(self):
        self.log = log.getChild('AssociationManager')
        self.log.debug('Initializing...')

    def get_association(self, association_id=None):
        if association_id is None:
            association_id = AvatarManager.get_instance().association_id
            if association_id is None:
                self.log.debug('No association found')
                return None

        self.log.debug('Constructing association data: %s' % association_id)

        result = {
            'members': [],
            'deputies': [],
            'rank': server.call('CorporationHighscoreInterface', 'getRank', [association_id]),
        }
        self.log.debug('Association rank: %s' % result['rank'])

        #r = server.call('CorporationHighscoreInterface', 'get', [35, 40])

        #r = server.call('CorporationInterface', 'getVCard', [[uuid]])

        r = server.call('CorporationInterface', 'get', [association_id])

        result['name'] = r['name']
        result['prestige'] = int(float(r['prestige']))
        for member in r['member']:
            result['members'].append(member['user_id'])
            if int(member['title']) == 0:
                result['chair'] = member['user_id']
            elif int(member['title']) == 1:
                result['deputies'].append(member['user_id'])

        return result

