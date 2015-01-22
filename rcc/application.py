# -*- coding:utf-8 -*-
"""Logic"""
import os
import sys
import getpass

import logging

from raillib.game import Game
from rcc.cli import CLI


class Application(object):
    def __init__(self, config):
        logging.debug('Creating application with config: %s' % str(config))

        self.current_handler = None
        self.avatar = None

        self.modules = {}
        # import all modules in rcc directory
        modules_dir = os.path.realpath(os.path.dirname(__file__))
        orig_sys_path = sys.path[:]
        sys.path.append(modules_dir)

        logging.debug('Start loading modules...')
        header = 'module_'
        for item in os.listdir(modules_dir):
            logging.debug('Found file: %s' % item)
            if item.startswith(header) and item.endswith(".py"):
                logging.debug("Importing file: %s" % item)
                module = __import__(os.path.basename(item)[:-3])
                logging.debug("Got thread: %s" % module.Module.name)
                self.modules[module.Module.name] = module.Module
        # # Restore system path
        sys.path = orig_sys_path

        logging.info('Loaded Threads: %s' % str(list(self.modules.keys())))

        logging.debug('Constructing Game object...')

        logging.debug('Application object successfully created.')

    def start(self):
        logging.info('Game is starting!')

        game = Game()

        print('Please login to Rail Nation.')
        game.authenticate(input('Email: '),
                          getpass.unix_getpass('Password: '))

        print('Select world to enter.')
        table = '%7s %3s %-12s'
        print(table % ('[ ID ]', 'Era', 'Name'))
        for world in game.get_worlds():
            print(table % (world.id, str(world.era), world.name))

        world_id = input('World ID: ')

        self.avatar = game.enter_world(world_id)
        logging.debug('Your ID: %s' % self.avatar.player_id)
        # logging.debug('Properties: %s' % self.avatar.properties)
        logging.debug('Client Info: %s' % self.avatar.client_info)
        logging.debug('Language: %s' % self.avatar.language)

        # Initialize Modules and start inner task-processing threads
        logging.debug('Starting threads')
        for module_name in self.modules.keys():
            self.modules[module_name] = self.modules[module_name](self.avatar)
            self.modules[module_name].start()

        cli = CLI(self.modules)
        # loop towards eternity
        while True:
            logging.debug('Current context: %s' %
                          cli.context)

            try:
                logging.debug('Waiting for input...')
                command = input(cli.prompt).split()
                logging.debug('Got input: %s' % str(command))

            except EOFError:
                self.end()
                return

            else:
                cli.process(command)

    def end(self):
        for t in self.modules.values():
            t.stop = True
            t.event.set()

        for t in self.modules.values():
            t.join()