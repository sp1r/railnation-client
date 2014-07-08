__author__ = 'spir'

from core import client


class Train:
    def __init__(self, tid):
        self.id = tid
        self.reliability = 0

    def update(self):
        data = client.get_train(self.id)
        data = data['Body']
        self.reliability = data['reliability']