# -*- coding:utf-8 -*-
"""docstring"""

from railnation.pages.railnation_page import BasicPage


class Page(BasicPage):
    def __init__(self):
        BasicPage.__init__(self)
        self.layout = [(0, 0, 'This is main page.'),
                       (1, 0, 'Don`t play with it!')]
        self.switch_key = 'M'