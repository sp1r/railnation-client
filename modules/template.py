# -*- coding:utf-8 -*-
"""docstring"""

import threading


class ModuleBase(threading.Thread):

    name = 'None'

    routes_in = ()

    def __init__(self, game):
        threading.Thread.__init__(self)
        self._running = True
        self._wake_up = threading.Event()
        self._timers = []
        self.api = {}
        self.game = game

    def set_attributes(self):
        pass

    def run(self):
        if self.name != 'auth':
            self.game.THREADS['auth'].authentication_passed.wait()

        self.set_attributes()

        while self._running:
            self._wake_up.clear()
            self.work()
            self._wake_up.wait()

        for t in self._timers:
            t.cancel()

    def work(self):
        pass

    def stop(self):
        self._running = False
        self._wake_up.set()

    def _set_timer(self, sleeping_period):
        timer = threading.Timer(sleeping_period, self._wake_me_up)
        timer.start()
        self._timers.append(timer)

    def _wake_me_up(self):
        self._wake_up.set()

    @property
    def prompt(self):
        return 'RN> '

    def enter(self, command):
        return None, None

    def execute(self, command):
        return None, None