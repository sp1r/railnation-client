# -*- coding:utf-8 -*-
"""
Interface for Page objects

Page should provide data enough to display it on screen, specify any
navigation zones and reaction to key pressing.

It may freely redraw itself as many times as it likes, but it must not
try to load any other pages. Such action must be performed via Application
instance only.
"""

example_help = (
    '"u" - upgrade current',
    '"s" - sell current',
    '"r" - return all to town'
)
example_layout = (
    (1, 10, 'Hello Little Brother! Welcome to my client!'),
    (5, 5, 'This is some random text.'),
    (12, 32, 'All this for testing only'),
    (21, 11, 'And not for real gaming'),
)
example_navigation = (
    (1, 10, 5, 'first'),
    (5, 5, 4, 'second'),
    (12, 32, 3, 'third'),
    (21, 11, 3, 'fourth'),
)


class BasicPage(object):
    """
      layout should consist of tuples (x, y, string), where x and y are
    relative coordinates inside the page area, and string does not contain
    any line breaks.
      navigation should consist of tuples (x, y, len, arg), where x and y are
    relative coordinates inside the page area, len - width of selection area,
    arg - parameter which will be passed to callback function
      help - is messages to instruct user of action keys
    """
    def __init__(self):
        self.layout = []
        self.navigation = []
        self.help = []

    def data_for_display(self):
        return self.layout, self.navigation, self.help