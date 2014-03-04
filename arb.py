#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
We will play this game as Gods. Oh yeah, we`ll do.
"""

__author__ = 'spir'

import multiprocessing as mp

from config import *

################################################################################
# Межпроцессорное взаимодействие

switch_ports = {}
bot_ports = {}

for name in bots.keys():
    if name == 'switch':
        continue
    switch_ports[name], bot_ports[name] = mp.Pipe()

###############################################################################

if __name__ == "__main__":
    subproc = {}

    instance = botlib.Switch(switch_ports)
    subproc['switch'] = mp.Process(target=instance, args=())
    subproc['switch'].start()

    instance = botlib.Messenger('game', bot_ports['game'], conn)
    subproc['game'] = mp.Process(target=instance, args=())
    subproc['game'].start()

    for bot_name in bots.keys():
        if bot_name in ['switch', 'main', 'test', 'game', 'research', 'repair']:
            continue
        instance = bots[bot_name](bot_name, bot_ports[bot_name])
        subproc[bot_name] = mp.Process(target=instance, args=())
        subproc[bot_name].start()

    while True:
        command = str(raw_input('arb> '))
        words = command.split(' ')
        if not words[0] in bots.keys():
            continue
        bot_ports['main'].send((words[0], 'main', 161, 0, words[1:]))

    subproc['switch'].join()