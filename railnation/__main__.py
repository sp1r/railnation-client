#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""Allow user to run Application as a module"""

import sys
if __package__ is None and not hasattr(sys, "frozen"):
    # It is a direct call to __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(path)))

import railnation

if __name__ == '__main__':
    sys.exit(railnation.main())