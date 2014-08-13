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
from railnation.core.railnation_app import Application
from railnation.core.railnation_errors import (
    ConnectionProblem,
    NotAuthorized,
)


def _signal_handler(signal, frame):
    """Callback for CTRL-C."""
    app.end()
    sys.exit(0)


def main():
    """Main entry point"""

    # Share global var
    global app

    try:
        app = Application()
    except ConnectionProblem as err:
        print('Got connection problem.')
        print(err)
        return 1
    except NotAuthorized as err:
        print(err)
        return 1

    # Catch the CTRL-C signal
    signal.signal(signal.SIGINT, _signal_handler)

    app.start()


if __name__ == '__main__':
    sys.exit(main())