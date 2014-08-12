# -*- coding:utf-8 -*-
"""Managing screen and data displaying"""

import curses
import os
import sys

from railnation.core.railnation_globals import (
    pages_path,
    orig_sys_path,
    log,
)


LEFT_BAR = 20
TOP_BAR = 3


class Screen(object):
    def __init__(self):
        self._init_curses()
        self.pages = {}
        self.pages_switch = {}
        self._load_all_pages()
        self.current_page = 'test'

    def _init_curses(self):
        # Init the curses screen
        self.screen = curses.initscr()
        if not self.screen:
            print("Error: Cannot init the curses library.\n")
            exit(1)

        # Set curses options
        curses.noecho()  # don`t print typed characters back to screen
        curses.cbreak()  # react on keypress instantly
        self.screen.keypad(1)  # enable keypad shortcuts

    def _load_all_pages(self):
        """import all pages in railnation.pages dir"""
        header = 'page_'
        for item in os.listdir(pages_path):
            if item.startswith(header) and item.endswith(".py"):
                log.debug("Importing file %s" % item)
                page_module = __import__(os.path.basename(item)[:-3])
                page_name = os.path.basename(item)[len(header):-3].lower()
                page = page_module.Page()
                self.pages[page_name] = page
                self.pages_switch[page.switch_key] = page_name
        # Restore system path
        sys.path = orig_sys_path

    def update(self):
        """Refresh screen data"""
        self.screen.erase()
        log.debug('Rewriting screen. Current page: %s' % self.current_page)
        self._draw_grid()
        self._draw_menu()
        self._draw_header()
        data = self.pages[self.current_page].data_for_display()
        log.debug('Page data: %s' % data)
        offset_x = LEFT_BAR + 1
        offset_y = TOP_BAR + 1
        for line in data['layout']:
            self.screen.addstr(line[0] + offset_y,
                               line[1] + offset_x,
                               line[2])
        self.screen.refresh()
        key = self.screen.getkey()
        if key in data['callbacks']:
            data['callbacks'][key]()
        elif key in self.pages_switch:
            self.current_page = self.pages_switch[key]

    def end(self):
        """restore normal terminal settings"""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def _draw_grid(self):
        max_y, max_x = self.screen.getmaxyx()
        self.screen.addstr(TOP_BAR, LEFT_BAR + 1, '-' * (max_x - LEFT_BAR - 1))
        for y in range(max_y):
            self.screen.addstr(y, LEFT_BAR, '|')

    def _draw_menu(self):
        self.screen.addstr(1, 5, 'PAGES:')
        for i, key in enumerate(self.pages_switch):
            if self.current_page == self.pages_switch[key]:
                self.screen.addstr(3 + i,
                                   1,
                                   '[%s]  %s' % (key, self.pages_switch[key]),
                                   curses.A_BOLD)
            else:
                self.screen.addstr(3 + i,
                                   1,
                                   '[%s] %s' % (key, self.pages_switch[key]))

    def _draw_header(self):
        self.screen.addstr(TOP_BAR - 2, LEFT_BAR + 2, 'Player: ')
        self.screen.addstr(TOP_BAR - 1, LEFT_BAR + 2, 'Corporation: ')
        self.screen.addstr(TOP_BAR - 2, LEFT_BAR + 31, 'Money: ')
        self.screen.addstr(TOP_BAR - 1, LEFT_BAR + 31, 'Prestige: ')
        self.screen.addstr(TOP_BAR - 2, LEFT_BAR + 62, 'Gold: ')
        self.screen.addstr(TOP_BAR - 1, LEFT_BAR + 62, 'Rank: ')