# -*- coding: utf-8 -*-

__author__ = 'spir'

import libgw


class Switch:
    """
    Класс, который поможет нам сэкономить на количестве пайпов при
    межпроцессорном взаимодействии.
    """
    def __init__(self):
        self.art = {}

    def add_port(self, name, pipe):
        self.art[name] = pipe

    def forward(self):
        """
        Направляет сообщения от одного процесса другому
        """
        for port in self.art.keys():

            while self.art[port].poll():
                packet = self.art[port].recv()
                print "Switching:", packet
                assert isinstance(packet, libgw.Packet)
                assert packet.destination_address in self.art.keys(), \
                    'Destination unknown'
                self.art[packet.destination_address].send(packet)