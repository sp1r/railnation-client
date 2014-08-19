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
from railnation.core.railnation_application import Application

from railnation.core.railnation_errors import (
    ConnectionProblem,
    NotAuthenticated,
)


def _signal_handler(signal, frame):
    """Callback for CTRL-C."""
    app.end()
    sys.exit(0)


def main():
    """Main entry point"""

    # Share global var
    global app

    # Catch the CTRL-C signal
    signal.signal(signal.SIGINT, _signal_handler)

    try:
        # load application parameters
        app = Application()
        app.start()
    except ConnectionProblem as err:
        print('Connection problem.')
        print(err)
        return 3
    except NotAuthenticated as err:
        print('Authentication problem.')
        print(err)
        return 2
    except RuntimeError as err:
        print(err)
        return 1


if __name__ == '__main__':
    sys.exit(main())