# -*- coding:utf-8 -*-
"""Main state of client"""

from railnation.pages.page_player import get_page


class MainModule:
    def __init__(self):
        self.money = 0
        self.science_points = 0

    def get_profile_page(self):
        return get_page()