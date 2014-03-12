# -*- coding: utf-8 -*-

__author__ = 'spir'

import multiprocessing as mp

import switch
import client
import libgw
import config
import modules.collect

# sorry me for that
hard_code = {
    'url': 'http://s6.railnation.ru/web/rpc/flash.php',
    'cookie': 'PHPSESSID=bs6net2jqk97kkk7vtsuu8sbk3',
    'checksum': '3caf8214532b258daf0118304972727e',
}


class Kernel:
    def __init__(self):
        self.switch = switch.Switch()
        self.interface = None
        self.game = client.Oracle(client.Engine(hard_code['url'],
                                                hard_code['cookie'],
                                                hard_code['checksum']))
        self.work_id = ""

    def __call__(self, *args, **kwargs):

        r = self.game.get_my_id()
        if r['Body']:
            self.work_id = str(r['Body'])
        else:
            raise Exception('Error! User is not logged in.')

        ports = {'query': 80}
        service_location = {'query': 'kernel'}

        local_port, switch_port = mp.Pipe()
        self.switch.add_port('kernel', switch_port)
        self.interface = libgw.KernelInterface('kernel', local_port)
        self.interface.ports = ports

        self.interface.listen[self.interface.ports['query']] = \
            self.process_query

        collect_port, switch_port = mp.Pipe()
        self.switch.add_port('collect', switch_port)
        new_interface = libgw.KernelInterface('collect', collect_port)
        new_interface.service_location = service_location
        new_interface.ports = ports
        module = modules.collect.Collect(libgw.KernelGateWay(new_interface))
        proc = mp.Process(target=module, args=())
        proc.start()

        while True:
            self.switch.forward()
            self.interface.process_requests()

    def process_query(self, data):
        method = data[0]

        if method == 'get_work_user':
            return self.game.get_user(self.work_id)

        assert hasattr(self.game, method), \
            " ".join(('Unknown function to call:', method))
        call = getattr(self.game, method)

        if len(data) > 1:
            return call(*data[1:])
        else:
            return call()
