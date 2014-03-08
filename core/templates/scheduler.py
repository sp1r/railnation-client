# -*- coding: utf-8 -*-
"""
Скелет модуля создающего расписание задач и выполняющий их по порядку.
"""

__author__ = 'spir'

from Queue import PriorityQueue
import time

from core.templates.module import Module
from core.templates.module import ModuleConfig


class SchedulerJob:
    """
    Класс, описывающий элементы приоритетной очереди задач.
    """
    def __init__(self, ready_at):
        """
        ready_at -- (int) момент времени, когда задание будет готово для
                    выполнения.
        """
        self.ready_at = ready_at

    def __cmp__(self, other):
        """
        Первыми в очереди будут задачи с меньшим временем ожидания.
        """
        return self.ready_at > other.ready_at


class SchedulerModuleConfig(ModuleConfig):
    def __init__(self):
        ModuleConfig.__init__(self)


class SchedulerModule(Module):
    def __init__(self, config):
        Module.__init__(self, config)

        self.schedule = PriorityQueue()
        self.current = None

    def bot_logic(self):
        # Если очередь пуста, перейти в режим ожидания
        if self.schedule.empty():
            self.config.hold = True
            return

        # Если не выбрана текущая задача, взять следующую из очереди
        if self.current is None:
            self.current = self.schedule.get()

        wait_time = self.current.ready_at - int(time.time())
        # Если текущая задача готова для обработки - обработать.
        if wait_time <= 0:
            self.process_job(self.current)
            self.current = None
        # Иначе - ожидать
        else:
            self.wait_for_message(wait_time)

    def process_job(self, job):
        raise NotImplementedError