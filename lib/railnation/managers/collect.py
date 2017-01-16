#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import logging


class CollectManager:
    """
    Manages bonuses collection from restaurant, mall and hotel.
    Both yours and your association.
    """
    instance = None

    @staticmethod
    def get_instance():
        if CollectManager.instance is None:
            CollectManager.instance = CollectManager()
        return CollectManager.instance

    def __init__(self):
        self.log = logging.getLogger('CollectManager')
        self.log.debug('Initializing...')
        self.schedule = {}

    def collect(self, building_id, player_id):
        # interface=BuildingInterface&method=collect
        # {"checksum":"e0cf78b7306751b66e07c2c43d5a9cc3","client":1,"parameters":[8,"d380ae55-938c-ad81-688b-46d471f534d7"],"hash":"2c7bdbf2077d34c6f6ff8017709eec46"}
        #
        # interface=BuildingInterface&method=getIFrame
        # {"checksum":"e0cf78b7306751b66e07c2c43d5a9cc3","client":1,"parameters":[],"hash":"d751713988987e9331980363e24189ce"}
        #
        # interface=BuildingInterface&method=videoWatched
        # {"checksum":"e0cf78b7306751b66e07c2c43d5a9cc3","client":1,"parameters":["d380ae55-938c-ad81-688b-46d471f534d7",8,"1483873839504d380ae55938cad81688b46d471f534d7","95cfdc536f9e86fd65a1afab3f8055e6"],"hash":"1c0835c13adfb2a7c74cf9c86c319e6c"}
        #
        #  http://media.oadts.com/www/delivery/xs.php?vrid=1483873839504d380ae55938cad81688b46d471f534d7-1483873678-0b0ecc3975c89c249ad021dc656db515&vaid=7e238e62e7a6a05048534a0cfea7c509&csid=17129-3590
        #  <?xml version="1.0"?><XSIGN><key>1483873839504d380ae55938cad81688b46d471f534d7</key><sign>95cfdc536f9e86fd65a1afab3f8055e6</sign></XSIGN>
        pass

    def watch_video(self, building_id, player_id):
        pass

    def watch_second_video(self, building_id, player_id):
        pass



