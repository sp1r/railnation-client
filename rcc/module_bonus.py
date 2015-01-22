# -*- coding:utf-8 -*-
"""docstring"""

import logging

from rcc.module import ModuleBase


REFRESH_PERIOD = 300


class Module(ModuleBase):
    name = 'bonus'

    routes_in = (
        ('show', 'bonus'),
        ('show', 'bonuses')
    )

    def __init__(self, avatar):
        ModuleBase.__init__(self)

        self.player = avatar.yourself

        self.range = []
        self.prompt = 'RN(bonus)> '

        self.blacklist = set()

    def enter(self, command):
        logging.debug('Entering module: Bonus')
        if len(command) == 1:
            print('argument required: all or mine')
            return None, None

        elif command[1] == 'mine':
            self.range = [self.player]
            self.prompt = 'RN(bonus-mine)> '
            logging.debug('Bonuses range: %s' % str(self.range))
            return self.name, self.prompt

        elif command[1] == 'all':
            corp = self.player.corporation
            if corp is None:
                self.range = [self.player]
            else:
                self.range = corp.members
            self.prompt = 'RN(bonus-all)> '
            logging.debug('Bonuses range: %s' % str(self.range))
            return self.name, self.prompt

    def execute(self, command):
        logging.debug('Executing module: Bonus')
        if len(command) == 0:
            return self.name, self.prompt

        elif command[0] == 'exit':
            return None, None

        elif command[0] == 'collect':
            self.collect()
            return self.name, self.prompt

        elif command[0] == 'show':
            self.show()
            return self.name, self.prompt

    def collect(self):
        logging.info('Start collecting bonuses.')

        for player in self.range:
            is_me = player.id == self.player.id
            buildings = player.collectables

            for b in buildings:
                # Hotel has simple collecting logic
                logging.debug('Player: %s Type: %2s Production time: %s' %
                              (player.name, b.type, b.production_time))

                if b.type == '10':
                    if b.bonus_ready:
                        result, bonus = b.collect(is_me)
                        if result == 0:
                            print('Bonus collected.')
                            if bonus is not None:
                                print('Got ticket! Prize: %s' % bonus)

                # Others and more complex
                else:
                    if b.bonus_ready and not b.owner_id in self.blacklist:
                        result, bonus = b.collect(is_me)
                        if result == 0:
                            print('Bonus collected.')
                            if bonus is not None:
                                print('Got ticket! Prize: %s' % bonus)
                        elif result == 10054:
                            self.blacklist.add(b.owner_id)

                    elif b.owner_id in self.blacklist and not b.bonus_ready:
                        self.blacklist.remove(b.owner_id)

    def show(self):
        logging.debug('Showing bonuses.')

        for player in self.range:
            buildings = player.collectables

            for b in buildings:
                print('Player: %s Type: %2s Amount: %7s Ready after: %5s' %
                      (player.name, b.type, b.effects, b.production_time))