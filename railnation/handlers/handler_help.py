# -*- coding:utf-8 -*-
"""docstring"""

from railnation.core.railnation_globals import screen
from railnation.core.railnation_screen import Page


class Handler:
    name = 'help'
    key = 'h'

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
            (10, 5, 'This program is a console client to browser '
                    'game Rail Nation (www.rail-nation.com) '
                    'by Travian games Inc.'),
            (11, 5, 'Due to specific of console communication '
                    'it has slightly different logic than web.'),
            (12, 5, 'And I`m trying to make things easier for player, '
                    'so he can concentrate on strategy instead of clicking.'),
            (13, 5, 'Hope you enjoy it.'),
            (16, 5, '<--- Left panel is for information'),
            (16, 10, 'It also contains menu.'),
            (17, 10, 'Go on and us it by pressing the key in square brackets'),
        )
        self.help_lines = (
            'In this section help messages will be shown,',
            'telling you about communicating with current screen.'
        )