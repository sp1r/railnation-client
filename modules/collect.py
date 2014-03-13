# -*- coding: utf-8 -*-
"""
Модуль, собирающий бонусы со станций участников ассоциации.
"""

_author__ = 'spir'

import time
import Queue


class Job():
    def __init__(self, building):
        self.building = building
        self.ready_at = time.time() + self.building.production_time

    def __cmp__(self, other):
        """
        Чем раньше будет готова задача, тем ближе она в очереди.
        """
        return self.ready_at > other.ready_at


class Collect:
    def __init__(self, kernel):
        self.kernel = kernel
        self.schedule = Queue.PriorityQueue()

    def __call__(self, *args, **kwargs):
        myself = self.kernel.get_current_player()
        mycorp = myself.corp()
        scope = mycorp.members()
        for player in scope:
            station = player.station()
            for btype in [9, 10, 11]:
                self.schedule.put(Job(station.buildings[btype]))

        while not self.schedule.empty():
            next_job = self.schedule.get()
            wait_time = next_job.ready_at - time.time()

            if wait_time > 0:
                time.sleep(wait_time)

            result = next_job.building.collect()
            next_job.building.refresh()
            if result == "success":
                print "collected!"
                got_prize = self.kernel.check_lottery()
                if got_prize:
                    reward = self.kernel.grab_ticket()
                    print reward
            elif result == "failure":
                if next_job.building.production_time == 0:
                    continue
                print 'missed'
            elif result == "overflow":
                next_job.building.production_time += 3600
                print 'bank overflow'

            self.schedule.put(Job(next_job.building))