# -*- coding:utf-8 -*-


class HandlerBase:
    name = ''

    def __init__(self, client):
        self.client = client

    def execute(self, command):
        pass

    def show(self):
        return 'something to show'

    def help(self):
        return 'this is help'