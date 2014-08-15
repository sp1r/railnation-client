# -*- coding:utf-8 -*-
"""Main menu management"""

example_menu = (
    '[W] Welcome page',
    '[A] Account page',
    '[T] Your trains',
)


class MainMenu:
    def __init__(self):
        self.menu = []
        self.pages = {}

    def get_menu(self):
        return self.menu

    def add_entry(self, ch, title, page_class):
        self.pages[ch] = page_class
        self.menu.append('[%s] %s' % (ch, title))


menu = MainMenu()