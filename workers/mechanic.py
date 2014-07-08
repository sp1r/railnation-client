__author__ = 'spir'

from workers import Worker


class Mechanic(Worker):
    def __init__(self, game):
        Worker.__init__(self)
        self.game = game
        self.name = "Mechanic"
        self.trains = game.get_myself().get_trains_list()

    def repair(self):
        for train in self.trains:
            train.update()

    def work(self):
        self.repair()
        return 270

    def __repr__(self):
        return "<Mechanic Worker>"