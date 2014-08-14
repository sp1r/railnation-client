# -*- coding:utf-8 -*-
"""Managing screen and data displaying"""

import curses
import time

from railnation.core.railnation_globals import log
from railnation.core.railnation_params import properties

LEFT_BAR = 30
INFOS_START = 4


class Screen(object):
    def __init__(self):
        self._init_curses()
        self.max_y, self.max_x = 0, 0
        self.min_y, self.min_x = 0, LEFT_BAR + 1

    def _init_curses(self):
        # Init the curses screen
        self.screen = curses.initscr()
        if not self.screen:
            raise RuntimeError("Cannot init screen.")

        # Set curses options
        curses.noecho()  # don`t print typed characters back to screen
        curses.cbreak()  # react on keypress instantly
        self.screen.keypad(True)  # enable keypad shortcuts
        curses.curs_set(0)  # make cursor invisible

    def update(self, infos, menu, body, navigation, help):
        """Refresh screen data"""
        self.screen.erase()
        log.debug('Reloading screen.')
        self.max_y, self.max_x = self.screen.getmaxyx()
        self._draw_template()
        self._draw_left_bar(infos, menu)
        self._draw_help(help)
        for item in body:
            self.screen.addstr(item[0] + self.min_y,
                               item[1] + self.min_x,
                               item[2])

        zones = self._translate_navigation(navigation)
        current_zone = 0
        self.screen.chgat(*zones[current_zone]['on'])
        self.screen.refresh()

        # Navigate trough zones
        got_action = False
        while not got_action:
            ch = self.screen.getch()
            if ch == curses.KEY_UP:
                self.screen.chgat(*zones[current_zone]['off'])
                current_zone = (current_zone - 1) % len(navigation)
            elif ch == curses.KEY_DOWN:
                self.screen.chgat(*zones[current_zone]['off'])
                current_zone = (current_zone + 1) % len(navigation)
            self.screen.chgat(*zones[current_zone]['on'])

        # if key in calls:
        #     calls[key]()
        # elif key in self.pages_switch:
        #     self.current_page = self.pages_switch[key]

    def end(self):
        """restore normal terminal settings"""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()

    def _draw_template(self):
        for y in range(self.max_y):
            self.screen.addstr(y, LEFT_BAR, '|')
        world_name = properties['client']['world_name']
        # world_name = 'Дымовая коробка'
        self.screen.addstr(1, (30 - len(world_name)) // 2, world_name)
        self.screen.addstr(2, 3, time.asctime())

    def _draw_left_bar(self, infos, menu):
        header = '= INFO ='
        current_line = INFOS_START
        self.screen.addstr(current_line, 0, LEFT_BAR * '-')
        self.screen.addstr(current_line, (LEFT_BAR - len(header)) // 2, header)
        current_line += 1
        for line in infos:
            self.screen.addstr(current_line, 2, line)
            current_line += 1
        current_line += 1
        header = '= MENU ='
        self.screen.addstr(current_line, 0, LEFT_BAR * '-')
        self.screen.addstr(current_line, (LEFT_BAR - len(header)) // 2, header)
        current_line += 1
        for line in menu:
            self.screen.addstr(current_line, 2, line)
            current_line += 1

    def _draw_help(self, help):
        self.screen.addstr(self.max_y - 1, 1, "press 'h' is for help")
        current_line = self.max_y - len(help)
        self.max_y -= current_line
        self.screen.addstr(current_line - 1,
                           LEFT_BAR + 1,
                           (self.max_x - LEFT_BAR) * '-')
        for line in help:
            self.screen.addstr(current_line, LEFT_BAR + 3, line)
            current_line += 1

    def _translate_navigation(self, navigation):
        translated = []
        for item in navigation:
            current = {
                'on': (item[0] + self.min_y, item[1] + self.min_x, item[2], curses.A_REVERSE),
                'off': (item[0] + self.min_y, item[1] + self.min_x, item[2], curses.A_NORMAL),
            }
            translated.append(current)
        return translated