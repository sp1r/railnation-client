# -*- coding:utf-8 -*-
"""docstring"""

import logging
import time
import random

import modules.template


REFRESH_PERIOD = 300


class Module(modules.template.ModuleBase):
    name = 'bonus'
    api = {
        'start': ('login', 'email', 'password'),
        'stop': ('get_worlds', ),
    }

    def set_attributes(self):
        self.player = self.game.avatar.me
        self.collecting = True
        self.blacklist = set()

    def work(self):
        if not self.collecting:
            return

        first = 99999
        for building in self.player.corporation.collectables:
            if building.bonus_ready:
                result, reward = building.collect(building.owner_id == self.player.id)
                if result == 10054:
                    # Bank overflow
                    logging.info('%s Overflows' % building.owner_id)
                elif not result["Body"]:
                    # already collected
                    logging.info('%s Missed' % building.owner_id)
                else:
                    # success
                    logging.info('%s Collected' % building.owner_id)
                    if reward is not None:
                        logging.info('Got Ticket! Reward: %s' % reward)

            else:
                if building.production_time < first:
                    first = building.production_time

            time.sleep(0.5)

        self._set_timer(first + random.randint(20, 60))

    def stop_collecting(self):
        self.collecting = False

    def start_collecting(self):
        self.collecting = True
        self._wake_up.set()

    # def collect(self):
    #     logging.info('Start collecting bonuses.')
    #
    #     for player in self.range:
    #         is_me = player.id == self.player.id
    #         buildings = player.collectables
    #
    #         for b in buildings:
    #             # Hotel has simple collecting logic
    #             logging.debug('Player: %s Type: %2s Production time: %s' %
    #                           (player.name, b.type, b.production_time))
    #
    #             if b.type == '10':
    #                 if b.bonus_ready:
    #                     result, bonus = b.collect(is_me)
    #                     if result == 0:
    #                         print('Bonus collected.')
    #                         if bonus is not None:
    #                             print('Got ticket! Prize: %s' % bonus)
    #
    #             # Others and more complex
    #             else:
    #                 if b.bonus_ready and not b.owner_id in self.blacklist:
    #                     result, bonus = b.collect(is_me)
    #                     if result == 0:
    #                         print('Bonus collected.')
    #                         if bonus is not None:
    #                             print('Got ticket! Prize: %s' % bonus)
    #                     elif result == 10054:
    #                         self.blacklist.add(b.owner_id)
    #
    #                 elif b.owner_id in self.blacklist and not b.bonus_ready:
    #                     self.blacklist.remove(b.owner_id)