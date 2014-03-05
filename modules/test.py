#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

from modules.module_templates.module import Bot


class Test(Bot):
    def __init__(self, name, pipe):
        Bot.__init__(self, name, pipe)

    def __call__(self):
        self.send_log(6, 'test test test')
        # self.send_msg('game', ('get_user', '3d4151da-515b-a98a-5d2f-b8b2627b6081'), True, self.hello, self.message_number)
        # self.send_msg('game', ('get_user', '3d4151da-515b-a98a-5d2f-b8b2627b6081'), True, self.hello, self.message_number)
        # self.send_msg('game', ('get_user', '3d4151da-515b-a98a-5d2f-b8b2627b6081'), True, self.hello, self.message_number)
        self.wait_for_message()

    def hello(self, data, number):
        print 'got some data:', data
        print 'my label is:', number