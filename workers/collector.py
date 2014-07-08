__author__ = 'spir'

from workers import Worker
import random


class Collector(Worker):
    def __init__(self, game):
        Worker.__init__(self)
        self.game = game
        self.name = "Collector"

    def collect(self):
        closest = 9999
        for building in self.game.get_myself().get_corporation().collectables():
            if building.production_time == 0:
                building.collect()
            elif building.production_time < closest:
                closest = building.production_time
        return closest + random.randint(20, 60)

    def work(self):
        return self.collect()

    def __repr__(self):
        return "<Collector Worker>"