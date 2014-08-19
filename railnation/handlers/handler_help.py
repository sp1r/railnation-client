# -*- coding:utf-8 -*-
"""docstring"""
from railnation.core.railnation_log import log
log.debug('Loading Handler: Help')

from railnation.core.railnation_globals import screen
from railnation.core.railnation_screen import Page


class Handler:
    name = 'help'
    key = 'h'
    menu = 'Help page'

    def __init__(self):
        self.page = HelpPage()

    def loop(self):
        while True:
            screen.display_page(self.page)
            screen.communicate()


class HelpPage(Page):
    def __init__(self):
        Page.__init__(self)
        self.layout = (
            (7, 4, 'This program is a console client to browser '
                    'game Rail Nation (www.rail-nation.com) '
                    'by Travian games Inc.'),
            (8, 4, 'Due to specific of console communication '
                    'it has slightly different logic than web.'),
            (9, 4, 'And I`m trying to make things easier for player, '
                    'so he can concentrate on strategy instead of clicking.'),
            (10, 4, 'Hope you enjoy it.'),
            (13, 2, '<--- Left panel is for information'),
            (14, 7, 'It also contains menu.'),
            (15, 7, 'Go on and us it by pressing the key in square brackets'),
        )
        self.help_lines = (
            '|  |  |',
            '|  |  |',
            'V  V  V',
            'In this section help messages will be shown,',
            'telling you about communicating with current screen.'
        )