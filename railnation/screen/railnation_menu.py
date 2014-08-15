# -*- coding:utf-8 -*-
"""Main menu management"""


class MainMenu:
    def __init__(self):
        self.entries = {}

    def add_entry(self, page_class):
        self.entries[page_class.key] = page_class

    def items(self):
        return self.entries.items()

    def __iter__(self):
        return self.entries.__iter__()

menu = MainMenu()