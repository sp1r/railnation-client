# -*- coding:utf-8 -*-
"""docstring"""

try:
    from queue import PriorityQueue
except ImportError:
    from Queue import PriorityQueue

import time
import threading


class ModuleBase(threading.Thread):
    name = 'Draft'

    routes_in = ()

    def __init__(self):
        threading.Thread.__init__(self)

        self.tasks = PriorityQueue()
        self.current_task = None

        self.lock = threading.Lock()
        self.event = threading.Event()

        self.stop = False

    def run(self):
        while not self.stop:
            # 1) if we have active task - put it back in queue
            # 2) try to get task with highest priority
            # 3) if we have none - wait for event
            # 4) if we have a task - wait till it is ready
            # 5) if we are waken up (by event) before task is ready - cycle
            # 6) if it is task time, do the task and dump it
            if self.current_task is not None:
                self.tasks.put(self.current_task)
                self.current_task = None

            if self.tasks.empty():
                self.event.wait()
                self.event.clear()

            else:
                self.current_task = self.tasks.get()
                wait_time = self.current_task.ready - int(time.time())
                self.event.wait(wait_time)
                if self.current_task.ready - int(time.time()) > 0:
                    self.event.clear()
                    continue
                else:
                    self.current_task.execute()
                    self.current_task = None

    def add_task(self, when_to_do, what_to_do, parameters):
        self.tasks.put(Task(when_to_do, what_to_do, parameters))
        self.event.set()

    def enter(self, command):
        return None, None

    def execute(self, command):
        return None, None


class Task(object):
    def __init__(self, fire_timestamp, function, parameters):
        self.ready = fire_timestamp
        self.target = function
        self.params = parameters

    def execute(self):
        return self.target(**self.params)

    def __lt__(self, other):
        return self.ready < other.ready

    def __eq__(self, other):
        return not self < other and not other < self

    def __ne__(self, other):
        return self < other or other < self

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self