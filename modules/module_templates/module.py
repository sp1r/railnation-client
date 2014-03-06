# -*- coding: utf-8 -*-

__author__ = 'spir'

import random


class ModuleConfig:
    """
    Переменные, управляющие работой модуля.
    И процедуры их изменения.

    Общение с другими модулями
    self.name -- (string) имя (адрес) модуля
    self.link -- (multiprocessing.Pipe) дуплексный канал обмена сообщениями

    self.service_ports -- (dict) номера портов, на которых работают службы.
    self.service_location -- (dict) имена (адреса) ботов предоставляющих службы.
    self.provided_services -- (dict) службы, которые предоставляет этот модуль.

    self.hold -- (bool) флаг переводящий модуль в режим ожидания
    """
    def __init__(self):
        """
        Значения по-умолчанию.
        """
        self.name = None
        self.link = None
        self.hold = False

        self.service_ports = {}
        self.service_location = {}
        self.provided_services = []
        self.required_services = []


class Module:
    """
    Модуль в основном состоит из 3-х частей: механизм общения с другими
    модулями, схема изменения внутреннего состояния и логика работы.

    Обмен данными соответствует упрощенной схеме UDP-датаграмм.
    Каждый модуль имеет имя, которое используется в качестве адреса при
    коммутации сообщений между ними, а так же число message_number, используемое
    в роли "случайного" номера порта при отправке сообщений.

    Таким образом сообщения, которыми обмениваются процессы имеют структуру:
        (destination_name, source_name,
        destination_port, source_port,
        data)

    Далее везде, что номера портов ниже 1024 используются для определенных
    заранее сервисов. А номера выше 1024 для выбора номеров при запросах.

    Примечание. message_number имеет тип <int>, то есть максимально мы сможем
    отправить чуть более 4 млрд сообщений.
    """
    def __init__(self, config):
        """
        Параметры модуля, для поддержки общения с другими модулями:
        self.message_number -- (int) счетчик сообщений
        self.listen -- (dict) указывает какие запросы будет обрабатывать модуль.
                    Ключами являются номера портов, значения - функции обработки
                    запросов.
        self.waiting --  (dict) содержит список отправленных запросов, на
                     которые модуль ждет ответ. Ключом является кортеж вида
                     (имя_модуля, номер_порта_запроса), значения - функция
                     обработки и дополнительные параметры.
        """
        assert isinstance(config, ModuleConfig)
        assert config.name is not None
        assert config.link is not None
        self.config = config

        self.message_number = random.randint(1025, 1000000)
        self.listen = {}
        self.waiting = {}

        print 'Module', self.config.name, 'initialized.'  # debugging

################################################################################
    #   Механизм обмена сообщениями

    def send_request(self, service_name, data,
                     reply_needed=False, callback=None, *args):
        """
        Отправляет сообщение удаленному сервису.
        Опционально устанавливает, что делать когда получен ответ на сообщение.

        Аргументы:
           service_name -- (string) имя сервиса, к которому происходит
                           обращение.
           data -- (any type) данные, которые будут отправлены
           reply_needed -- (bool) флаг, показывающий ожидать ли
                           ответа на это сообщение
           callback -- (callable) функция, которая будет вызвана, когда будет
                       получен ответ, данные из ответа будут переданы ей
           args -- (iterable) дополнительные аргументы, которые будут переданы
                   функции обработки ответа
        """
        assert service_name in self.config.service_location.keys()
        assert self.config.service_location[service_name] is not None
        destination_name = self.config.service_location[service_name]
        assert service_name in self.config.service_ports.keys()
        destination_port = self.config.service_ports[service_name]

        if reply_needed:
            assert callback is not None
            # ждать, когда придет сообщение от модуля 'destination_name' на
            # сообщение с номером 'self.message_number'
            wanted_message = (destination_name, self.message_number)
            self.waiting[wanted_message] = (callback, args)

        packet = (destination_name,
                  self.config.name,
                  destination_port,
                  self.message_number,
                  data)
        self.config.link.send(packet)
        self.message_number += 1

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
        packet = (destination_name,
                  self.config.name,
                  destination_port,
                  source_port,
                  data)
        self.config.link.send(packet)

    def _process_one_message(self):
        """
        Прочитать и обработать одно сообщение из канала.
        Канал должен содержать хотя бы одно сообщение. Иначе мы тут зависнем,
        а мы этого не хотим. Подождать можно в другом месте.

        Если не существуют инструкции по обратокте этого сообщения в
        self.listen, либо в self.waiting сообщение будет отброшено.
        """
        assert self.config.link.poll()

        packet = self.config.link.recv()
        destination, source, destination_port, source_port, data = packet
        assert destination == self.config.name, \
            " ".join(('Msg for', destination, 'got by', self.config.name))

        # Если это обращение к собственному сервису:
        if destination_port in self.listen.keys():
            process_function = self.listen[destination_port]
            reply = process_function(data)
            if reply is not None:
                self.send_reply(source, source_port, destination_port, reply)

        # Если это ответ на наше сообщение
        elif (source, destination_port) in self.waiting.keys():
            callback, args = self.waiting[(source, destination_port)]
            callback(data, *args)
            del self.waiting[(source, destination_port)]

    def get_all_messages(self):
        """
        Обрабатывает все сообщения, имеющиеся в канале на данный момент.
        """
        while self.config.link.poll():
            self._process_one_message()

    def wait_for_message(self, timeout=None):
        """
        Ожидает получения любого сообщения.

        Аргументы:
           timeout -- (int) количество секунд, в течение которых будет ожидаться
                      сообщение. По умолчанию - ожидать бесконечно.
        """
        if self.config.link.poll(timeout):
            self._process_one_message()

    def wait_all_replies(self):
        """
        Ожидает получения всех ответов на отправленные запросы
        """
        while self.waiting:
            self.wait_for_message()

################################################################################
    #   Логика работы

    def __call__(self):
        """
        Для начала работы, модуль должен быть вызван.
        """
        print 'Module', self.config.name, 'started.'  # debugging
        self.open_ports()
        self.configure()
        while True:
            if self.config.hold:
                self.wait_for_message()
            else:
                self.bot_logic()

    def open_ports(self):
        """
        Определяет обработчики для входящих сообщений.
        """
        self.listen[self.config.service_ports['control']] = self.change_state

    def configure(self):
        """
        Одноразовые настроечные процедуры.
        """
        raise NotImplementedError

    def bot_logic(self):
        """
        Главный сценарий работы.
        """
        raise NotImplementedError

################################################################################
    #   Изменение состояния

    def change_state(self, data):
        """
        Обработчик команд управления.
        """
        raise NotImplementedError

################################################################################
#   Дополнительные функции

    def require_attr(self, attr_name, service_name, request, callback, *args):
        """
        Обрабатывает ситауцию необходимости получения значения локального
        аттрибута от другого модуля перед продолжением работы.
        Запрашивает данные, дожадается ответа и устанавливает свой аттрибут
        в определенное значение на основании этих данных

        Аргументы:
           attr_name -- (string) имя аттрибута, который необходимо установить
           service_name -- (string) имя сервиса, которому нужно отправить запрос
           request -- запрос в формате, поддерживаемом модулем-получателем
           callback -- (callable) функция, которая обработает ответ и установит
                        локальный параметр
           args -- (iterable) дополнительные аргументы, которые будут переданы
                   функции обработки ответа
        """
        setattr(self, attr_name, None)
        self.send_request(service_name, request, True, callback, *args)
        while getattr(self, attr_name) is None:
            self.wait_for_message()