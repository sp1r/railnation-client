# -*- coding: utf-8 -*-

__author__ = 'spir'

import Queue
import random
import time

import callback


class Packet:
    def __init__(self, daddr, saddr, dport, sport, payload):
        self.destination_address = daddr
        self.source_address = saddr
        self.destination_port = dport
        self.source_port = sport
        self.payload = payload

    def __repr__(self):
        return ', '.join((self.destination_address,
                          self.source_address,
                          str(self.destination_port),
                          str(self.source_port),
                          str(self.payload)))


class KernelInterface:
    def __init__(self, name, pipe):
        self.link = pipe
        self.address = name

        self.ports = {}
        self.service_location = {}
        self.provided_services = []
        self.required_services = []

        self.message_number = random.randint(1025, 1000000)
        self.listen = {}
        self.waiting = {}

        self.buffer = Queue.Queue()

    def get(self, service_name, data, callback, *args):
        """
        Отправляет сообщение удаленному сервису и дожидается ответа.

        Аргументы:
           service_name -- (string) имя сервиса, к которому происходит
                           обращение.
           data -- (any type) данные, которые будут отправлены
           callback -- (callable) функция, которая будет вызвана, когда будет
                       получен ответ, данные из ответа будут переданы ей
           args -- (iterable) дополнительные аргументы, которые будут переданы
                   функции обработки ответа
        """
        assert service_name in self.service_location.keys()
        assert self.service_location[service_name] is not None
        destination_name = self.service_location[service_name]

        assert service_name in self.ports.keys()
        destination_port = self.ports[service_name]

        packet = Packet(daddr=destination_name,
                        saddr=self.address,
                        dport=destination_port,
                        sport=self.message_number,
                        payload=data)
        self.link.send(packet)

        # ждать, когда придет сообщение от модуля 'destination_name' на
        # порт 'self.message_number'
        while True:
            packet = self.wait_for_message()
            if packet.source_address == destination_name and \
                    packet.destination_port == self.message_number:
                self.message_number += 1
                return callback(packet.payload, *args)
            else:
                self.buffer.put(packet)

    def send_reply(self, destination_name, destination_port, source_port, data):
        """
        Отправляет ответ определенному модулю на его запрос.

        Аргументы:
           destination_name -- (string) имя модуля, которому отправляется
                               ответ.
           destination_port -- (int) номер порта, на который отправляется ответ.
           source_port -- (int) номер порта, c которого отправляется ответ.
           producing_service_name -- (string) имя сервиса, который формирует
                                     ответ.
           data -- (any type) данные, которые будут отправлены
        """
        packet = Packet(daddr=destination_name,
                        saddr=self.address,
                        dport=destination_port,
                        sport=source_port,
                        payload=data)
        self.link.send(packet)

    def process_one_message(self):
        """
        Прочитать и обработать одно сообщение из канала.
        Канал должен содержать хотя бы одно сообщение. Иначе мы тут зависнем,
        а мы этого не хотим. Подождать можно в другом месте.

        Если не существуют инструкции по обратокте этого сообщения в
        self.listen, либо в self.waiting сообщение будет отброшено.
        """
        assert self.link.poll()

        packet = self.link.recv()
        assert isinstance(packet, Packet)
        assert packet.destination_address == self.address, \
            " ".join(('Msg for', packet.destination_address,
                      'got by', self.address))

        packet_label = (packet.source_address, packet.destination_port)

        # Если это обращение к собственному сервису:
        if packet.destination_port in self.listen.keys():
            process_function = self.listen[packet.destination_port]
            reply = process_function(packet.payload)
            if reply is not None:
                self.send_reply(packet.source_address,
                                packet.source_port,
                                packet.destination_port,
                                reply)

        # Если это ответ на наше сообщение
        elif packet_label in self.waiting.keys():
            callback, args = self.waiting[packet_label]
            callback(packet.payload, *args)
            del self.waiting[packet_label]

    def get_all_messages(self):
        """
        Обрабатывает все сообщения, имеющиеся в канале на данный момент.
        """
        while self.link.poll():
            yield self.link.recv()

    def wait_for_message(self, timeout=None):
        """
        Ожидает получения любого сообщения.

        Аргументы:
           timeout -- (int) количество секунд, в течение которых будет ожидаться
                      сообщение. По умолчанию - ожидать бесконечно.
        """
        if self.link.poll(timeout):
            return self.link.recv()
        return None

    def process_requests(self):
        for packet in self.get_all_messages():
            self.buffer.put(packet)
        while not self.buffer.empty():
            packet = self.buffer.get()
            if not packet.destination_port in self.listen.keys():
                print 'Unknown port', packet.destination_port
            else:
                callback = self.listen[packet.destination_port]
                data = callback(packet.payload)
                if data is not None:
                    reply = Packet(daddr=packet.source_address,
                                   saddr=self.address,
                                   dport=packet.source_port,
                                   sport=packet.destination_port,
                                   payload=data)
                    self.link.send(reply)

    def listen(self):
        """
        Ожидает получения всех ответов на отправленные запросы
        """
        while self.waiting:
            self.wait_for_message()


class KernelGateWay:
    def __init__(self, interface):
        assert isinstance(interface, KernelInterface)
        self.interface = interface

    def sleep(self, timeout=None):
        if timeout is not None:
            return_time = int(time.time()) + timeout
            wait_time = return_time - int(time.time())
            while wait_time > 0:
                self.interface.wait_for_message(wait_time)
                wait_time = return_time - int(time.time())
        else:
            self.interface.wait_for_message()

    def register_listener(self, service, function):
        self.interface.listen[self.interface.ports[service]] = function

    def get_current_player(self):
        return self.interface.get('query',
                                  ('get_work_user', ),
                                  callback.parse_player,
                                  self)

    def get_player(self, player_id):
        return self.interface.get('query',
                                  ('get_user', player_id),
                                  callback.parse_player,
                                  self)

    def get_corp(self, corp_id):
        return self.interface.get('query',
                                  ('get_corp', corp_id),
                                  callback.parse_corp,
                                  self)

    def get_station(self, owner_id):
        return self.interface.get('query',
                                  ('get_buildings', owner_id),
                                  callback.parse_station,
                                  self, owner_id)

    def collect(self, player_id, building_type):
        return self.interface.get('query',
                                  ('collect', player_id, building_type),
                                  callback.parse_collecting_result)

    def check_lottery(self):
        return self.interface.get('query',
                                  ('check_lottery', ),
                                  callback.parse_lottery)