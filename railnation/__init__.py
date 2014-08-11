#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Initialize software"""

__appname__ = 'railnation'
__version__ = '0.0.0'
__author__ = 'V.Spiridonov <namelessorama@gmail.com>'
__license__ = ''

# import system libs
import signal
import sys

# import own libs
from railnation.core.railnation_game import Game


def _signal_handler(signal, frame):
    """Callback for CTRL-C."""
    game.end()
    sys.exit(0)


def main():
    """Main entry point"""

    # Share global var
    global game

    game = Game()

    # Catch the CTRL-C signal
    signal.signal(signal.SIGINT, _signal_handler)

    game.start()


if __name__ == '__main__':
    sys.exit(main())