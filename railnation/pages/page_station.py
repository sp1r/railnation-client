# -*- coding:utf-8 -*-
"""docstring"""

from railnation.pages.railnation_page import BasicPage


class Page(BasicPage):
    def __init__(self):
        BasicPage.__init__(self)
        self.layout = [(0, 0, 'This is stations page.'),
                       (1, 0, 'Currently in development...')]
        self.switch_key = 'S'