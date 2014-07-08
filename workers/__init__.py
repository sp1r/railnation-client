__author__ = 'spir'


class Worker:
    def __init__(self):
        self.name = "Worker"

    def __lt__(self, other):
        return self.name < other.name

    def work(self, *args, **kwargs):
        raise NotImplementedError