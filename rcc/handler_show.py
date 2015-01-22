# -*- coding:utf-8 -*-
"""docstring"""


class Handler(object):
    name = 'show'

    def __init__(self, avatar):
        self.avatar = avatar
        self.context = 'show'

    def execute(self, command):
        if len(command) < 2:
            return None

        if command[1] == 'trains':
            self.show_trains()

        return None

    def show_trains(self):
        for train in sorted(self.avatar.yourself.trains):
            print(train.type, train.id, train.reliability,
                  train.profit_last_hour, train.bought)