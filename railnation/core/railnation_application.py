# -*- coding:utf-8 -*-
"""Logic"""

import time

from railnation.core.railnation_globals import log

# import railnation.core.railnation_client  # creates client instance

from railnation.core.railnation_auth import authorize
from railnation.core.railnation_params import load_game

from railnation.core.railnation_screen import Screen

test_infos = (
    'Name: Dr. Frankenstein',
    'Copr: Газетчики',
    'Prestige: 1 234 567',
    'Rank: 12 343',
    'Money: 50 000 000',
    'Gold: 15 000'
)
test_menu = (
    '[W] Welcome page',
    '[A] Account page',
    '[T] Your trains'
)
test_help = (
    '"u" - upgrade current',
    '"s" - sell current',
    '"r" - return all to town'
)
test_body = (
    (1, 10, 'Hello Little Brother! Welcome to my client!'),
    (5, 5, 'This is some random text.'),
    (12, 32, 'All this for testing only')
)
test_navigation = (
    (1, 10, 10, 'first'),
    (5, 3, 4, 'second'),
    (11, 32, 7, 'third')
)


class Application(object):
    def __init__(self):
        log.info('Application object created.')

        # load components here (?)

        print('Authorizing on rail-nation.com...')
        authorize()
        log.info('Authorization complete.')

        print('Loading game parameters...')
        load_game()
        log.info('Game parameters loaded.')

        self.screen = Screen()
        log.info('Screen ready.')

    def start(self):
        log.info('Game is starting!')
        self.screen.update(test_infos, test_menu, test_body, test_navigation, test_help)

        while True:
            # ch = self.screen.get_input(timeout=0.1)
            # if ch:
            #     pass
            # else:
            #     pass

            self.screen.update(test_infos, test_menu, test_body, test_navigation, test_help)
            time.sleep(0.5)

    def end(self):
        self.screen.end()
