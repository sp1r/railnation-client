#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
We will play this game as Gods. Oh yeah, we`ll do.
"""

__author__ = 'spir'

import multiprocessing as mp

from modules.module_templates import ModuleConfig
import config
import modules

###############################################################################

if __name__ == "__main__":

    switch_config = modules.SwitchConfig()
    my_pipe, switch_config.art[config.main_module_name] = mp.Pipe()

    subproc = {}
    service_location = {}
    clear_to_start = True

    for module_description in config.load_modules:
        module_name, module_class, module_config = module_description

        # inform module, how to communicate with others:
        assert isinstance(module_config, ModuleConfig)
        module_config.name = module_name
        module_config.link, switch_config.art[module_name] = mp.Pipe()

        # register module`s services:
        for service in module_config.provided_services:
            service_location[service] = module_name

        # check dependencies:
        for service in module_config.required_services:
            if not service in service_location.keys():
                print "Broken dependency:", service, \
                    'not found for', module_name
                clear_to_start = False

        # inform module, how to use services:
        module_config.service_ports = config.service_ports
        module_config.service_location = service_location

        instance = module_class(module_config)
        subproc[module_name] = mp.Process(target=instance, args=())

    switch = modules.Switch(switch_config)
    subproc['switch'] = mp.Process(target=switch, args=())

    if clear_to_start:
        for module in subproc.keys():
            subproc[module].start()

        while True:
            command = str(raw_input('arb> '))
            words = command.split(' ')
            if not words[0] in subproc.keys():
                continue
            my_pipe.send((words[0], 'main',
                          config.service_ports['control'], 0,
                          words[1:]))

        subproc['switch'].join()
    else:
        print 'Check dependencies. May be change modules loading order?'
    # subproc = {}
    #
    # instance = modules.Switch(switch_ports)
    # subproc['switch'] = mp.Process(target=instance, args=())
    # subproc['switch'].start()
    #
    # instance = modules.Messenger('game', bot_ports['game'], conn)
    # subproc['game'] = mp.Process(target=instance, args=())
    # subproc['game'].start()
    #
    # for bot_name in bots.keys():
    #     if bot_name in ['switch', 'main', 'test', 'game', 'research', 'repair']:
    #         continue
    #     instance = bots[bot_name](bot_name, bot_ports[bot_name])
    #     subproc[bot_name] = mp.Process(target=instance, args=())
    #     subproc[bot_name].start()
    #
