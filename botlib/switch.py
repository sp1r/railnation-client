#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'


class Switch:
    """
    Класс, который поможет нам сэкономить на количестве пайпов при
    межпроцессорном взаимодействии.
    """
    def __init__(self, art):
        """
        art -- Address Resolution Table, словарь вида:
            { имя : pipe, ... }
        """
        assert type(art) is dict
        self.art = art

    def __call__(self):
        """
        Направляет сообщения от одного процесса другому
        """
        while True:

            for port in self.art.keys():

                while self.art[port].poll():
                    packet = self.art[port].recv()
                    print "Switching:", packet
                    assert packet[0] in self.art.keys(), 'Destination unknown'
                    self.art[packet[0]].send(packet)