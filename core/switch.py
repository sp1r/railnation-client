# -*- coding: utf-8 -*-

__author__ = 'spir'


class SwitchConfig:
    def __init__(self):
        """
        art -- Address Resolution Table, словарь вида:
            { имя : pipe, имя : pipe, ... }
        """
        self.art = {}

    def add_port(self, name, pipe):
        self.art[name] = pipe


class Switch:
    """
    Класс, который поможет нам сэкономить на количестве пайпов при
    межпроцессорном взаимодействии.
    """
    def __init__(self, config):
        assert isinstance(config, SwitchConfig)
        self.config = config

    def __call__(self):
        """
        Направляет сообщения от одного процесса другому
        """
        print 'Switch activated.'
        while True:

            for port in self.config.art.keys():

                while self.config.art[port].poll():
                    packet = self.config.art[port].recv()
                    print "Switching:", packet
                    assert packet[0] in self.config.art.keys(), \
                        'Destination unknown'
                    self.config.art[packet[0]].send(packet)