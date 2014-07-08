# -*- coding: utf-8 -*-
"""
Single Process, Single Queue

Модель рабочего выполняющегося в одном процессе с одной общей очередью задач.

Очередь представляет собой расписание действий, которые должны быть выполнены.
Каждое действие должно включать в себя ряд параметров:
1) что должно быть сделано (функция)
2) какие требования должны быть выполнены перед запуском (например, наличие достаточного количества денег)
3) величина отсрочки выполнения, при несоблюдении требований
"""
__author__ = 'sp1r'

import time
from queue import PriorityQueue
from threading import Thread

from core.base import log


class SPSQ(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.schedule = PriorityQueue()
        self.next_run = 0
        self.next_worker = None

    def register_worker(self, worker):
        self.schedule.put((0, worker))

    def run(self):
        while True:
            if self.next_run > 0:
                time.sleep(self.next_run)

            if self.next_worker is not None:
                delay = self.next_worker.work()
                self.schedule.put((delay, self.next_worker))

            self.next_run, self.next_worker = self.schedule.get()
            log.debug("Next run in %d. Next worker: %s" % (self.next_run, repr(self.next_worker)))

if __name__ == "__main__":
    pass