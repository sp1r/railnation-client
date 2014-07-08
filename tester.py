#-*- coding: utf-8 -*-
__author__ = 'spir'

from core.auth import quick_login
from managers.spsq import SPSQ
from workers.collector import Collector
from workers.mechanic import Mechanic

if __name__ == "__main__":
    game = quick_login()

    col = Collector(game)
    mec = Mechanic(game)
    m = SPSQ()
    m.register_worker(col)
    m.register_worker(mec)
    m.start()
    m.join()