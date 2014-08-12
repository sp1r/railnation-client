# -*- coding:utf-8 -*-
"""docstring"""

from railnation.pages.railnation_page import BasicPage


class Page(BasicPage):
    def __init__(self):
        BasicPage.__init__(self)
        self.layout = [(1, 1, 'Hello wolf! Test page'),
                       (2, 1, 'Press "a" for magic!')]
        self.switch_key = 'Z'
        self.key_map = {'a': self.press_a}

    def press_a(self):
        self.layout.append((len(self.layout) + 1, 3, 'One more press of "a"'))