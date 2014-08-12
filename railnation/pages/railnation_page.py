# -*- coding:utf-8 -*-
"""Interface from Screen to Page"""


class BasicPage(object):
    """
    layout should consist of tuples (x, y, string), where x and y are
    relative coordinates inside the page area, and string does not contain
    any line breaks.
    """
    def __init__(self):
        self.layout = []
        self.max_x = lambda: max([len(i[2]) + i[1] for i in self.layout])
        self.max_y = lambda: max([i[0] for i in self.layout]) + 1
        self.key_map = {}
        self.switch_key = ''

    def data_for_display(self):
        return {
            'layout': self.layout,
            'max_y': self.max_x,
            'max_x': self.max_y,
            'callbacks': self.key_map,
        }