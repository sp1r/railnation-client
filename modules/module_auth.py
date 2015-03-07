# -*- coding:utf-8 -*-
"""docstring"""

import threading

import modules.template

from railnationlib.game import Avatar


class Module(modules.template.ModuleBase):
    name = 'auth'
    api = {
        'login': ('login', 'email', 'password'),
        'list': ('get_worlds', ),
        'world': ('make_avatar', 'world_id'),
        'show': ('is_authenticated', ),
    }

    def set_attributes(self):
        self.authentication_passed = threading.Event()

    def login(self, email, password):
        if self.game.client.authenticated:
            return 'already OK'

        self.game.client.authenticate(email, password)

        if self.game.client.authenticated:
            return 'OK'
        else:
            return 'Error'

    def get_worlds(self):
        return self.game.client.get_worlds()

    def make_avatar(self, world_id):
        self.game.client.enter_world(world_id)
        self.game.avatar = Avatar(self.game.client)
        if self.game.avatar is not None:
            self.authentication_passed.set()
            return 'OK'
        else:
            return 'Error'

    def is_authenticated(self):
        return self.game.client.authenticated