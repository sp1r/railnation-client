# -*- coding:utf-8 -*-
"""
Managing screen and data displaying.
Define displaying basic classes (Page, Table).
"""

import curses
import time

from railnation.core.railnation_log import log
log.debug('Loading module: Screen')

from railnation.core.railnation_errors import (
    ChangeHandler,
    WindowTooSmall,
)

MIN_WIDTH = 80
MIN_HEIGHT = 24

LEFT_BAR = 30
INFOS_START = 4


class Screen(object):
    """
    menu and infos -- are components of UI common to all pages.

    Core methods are:
    display_plain -- to print text without anything else
    display_page -- to draw a Page object to screen with gui
    display_table -- to draw a Table object to screen with gui
    """
    def __init__(self, menu, infos):
        self._init_curses()
        self.max_y, self.max_x = 0, 0
        self.min_y, self.min_x = 0, LEFT_BAR + 1

        self.navigate = False
        self.zones = []
        self.current_zone = 0

        self.menu = menu
        self.infos = infos

    def _init_curses(self):
        """Init the screen"""
        self.screen = curses.initscr()
        if not self.screen:
            raise RuntimeError("Cannot init screen.")

        curses.noecho()  # don`t print typed characters back to screen
        curses.cbreak()  # react on keypress instantly
        curses.curs_set(0)  # make cursor invisible
        self.screen.move(0, 0)  # park cursor
        self.screen.keypad(1)  # enable keypad shortcuts
        self.screen.timeout(100)  # input timeout in ms

    def end(self):
        """Restore normal terminal settings"""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()

    def min_resolution_satisfied(self):
        self.max_y, self.max_x = self.screen.getmaxyx()
        log.debug('Screen size: %s x %s' % (self.max_x, self.max_y))
        return self.max_y >= MIN_HEIGHT and self.max_x >= MIN_WIDTH

    def display_plain(self, text):
        """Print text line without gui"""
        self.screen.erase()
        log.debug('Reloading screen. Will draw plain text.')

        self.max_y, self.max_x = self.screen.getmaxyx()
        log.debug('Screen size: %s x %s' % (self.max_x, self.max_y))

        if self.max_y < 1:
            return

        if self.max_x < len(text):
            self.screen.addstr(0, 0, text[:self.max_x])
        else:
            self.screen.addstr(0, 0, text)

        self.screen.refresh()

    def display_page(self, page):
        """Draw a page with gui"""
        assert isinstance(page, Page)

        self.screen.erase()
        log.debug('Reloading screen. Will draw a page.')

        if not self.min_resolution_satisfied():
            raise WindowTooSmall()

        self._draw_left_bar()

        if page.help_lines:
            self._draw_help(page.help_lines)

        self._draw_page_body(page.layout)

        if page.navigation:
            self.navigate = True
            self.zones = self._translate_navigation(page.navigation)
            self.current_zone = 0
            self.screen.chgat(*self.zones[self.current_zone]['on'])
        else:
            self.navigate = False

        self.screen.refresh()

    def display_table(self, table):
        """Draw a table with gui"""
        assert isinstance(table, Table)

        self.screen.erase()
        log.debug('Reloading screen. Will draw a table.')

        if not self.min_resolution_satisfied():
            raise WindowTooSmall()

        self._draw_left_bar()

        if table.help_lines:
            self._draw_help(table.help_lines)

        self._draw_table_body(table.header, table.rows)

    def communicate(self, actions=None):
        if actions is None:
            actions = ()

        while True:
            ch = self.screen.getch()

            if ch == -1:
                continue

            elif ch == curses.KEY_UP and self.navigate:
                self.screen.chgat(*self.zones[self.current_zone]['off'])
                current_zone = (self.current_zone - 1) % len(self.zones)
                self.screen.chgat(*self.zones[current_zone]['on'])

            elif ch == curses.KEY_DOWN and self.navigate:
                self.screen.chgat(*self.zones[self.current_zone]['off'])
                current_zone = (self.current_zone + 1) % len(self.zones)
                self.screen.chgat(*self.zones[current_zone]['on'])

            elif chr(ch) in actions:
                if self.navigate:
                    actions[chr(ch)](*self.zones[self.current_zone]['args'])
                else:
                    actions[chr(ch)]()

            elif chr(ch) in self.menu:
                raise ChangeHandler(self.menu[chr(ch)])

            elif chr(ch) == 'h':
                raise ChangeHandler('help')

    def _draw_left_bar(self):
        for y in range(self.max_y):
            self.screen.addstr(y, LEFT_BAR, '|')
        #world_name = properties['client']['world_name']
        world_name = 'Hello Wolf!'
        self.screen.addstr(1, (30 - len(world_name)) // 2, world_name)
        self.screen.addstr(2, 3, time.asctime())

        header = '= INFO ='
        current_line = INFOS_START
        self.screen.addstr(current_line, 0, LEFT_BAR * '-')
        self.screen.addstr(current_line, (LEFT_BAR - len(header)) // 2, header)
        current_line += 1
        for line in self.infos.get_infos():
            self.screen.addstr(current_line, 2, line)
            current_line += 1
        current_line += 1
        header = '= MENU ='
        self.screen.addstr(current_line, 0, LEFT_BAR * '-')
        self.screen.addstr(current_line, (LEFT_BAR - len(header)) // 2, header)
        current_line += 1
        for key, item in self.menu.items():
            self.screen.addstr(current_line, 2, '[%s] %s' % (key, item))
            current_line += 1

        self.screen.addstr(self.max_y - 1, 1, "press 'h' for help")

    def _draw_help(self, help_lines):
        self.max_y -= len(help_lines) + 1
        self.screen.addstr(self.max_y,
                           LEFT_BAR + 1,
                           (self.max_x - LEFT_BAR) * '-')
        for position, line in enumerate(help_lines):
            self.screen.addstr(self.max_y + position + 1, LEFT_BAR + 3, line)

    def _draw_page_body(self, body):
        for item in body:
            self.screen.addstr(item[0] + self.min_y,
                               item[1] + self.min_x,
                               item[2])

    def _draw_table_body(self, header, rows):
        pass

    def _translate_navigation(self, navigation):
        translated = []
        for item in navigation:
            current = {
                'on': (item[0] + self.min_y, item[1] + self.min_x, item[2], curses.A_REVERSE),
                'off': (item[0] + self.min_y, item[1] + self.min_x, item[2], curses.A_NORMAL),
                'args': navigation[3:],
            }
            translated.append(current)
        return translated


class Page:
    """Pre-formatted page"""
    def __init__(self):
        self.title = ''
        self.layout = []
        self.navigation = []
        self.help_lines = []


class Table:
    """Bunch of rows"""
    def __init__(self):
        self.title = ''
        self.help_lines = []
        self.header = []
        self.rows = []