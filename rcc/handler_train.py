# -*- coding:utf-8 -*-
"""docstring"""


class Handler(object):
    name = 'train'

    def __init__(self, avatar):
        self.avatar = avatar
        self.context = 'train'

    def execute(self, command):
        return self