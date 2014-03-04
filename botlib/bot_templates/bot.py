#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'spir'

import time


class Bot:
    """
    Бот в основном состоит из 3-х частей: механизм общения с другими ботами,
    схема изменения внутреннего состояния и собственно логика работы.

    Обмен данными соответствует упрощенной схеме UDP-датаграмм.
    Каждый бот имеет имя, которое используется для коммутации сообщений
    между ними, а так же число message_number, используемое в роли порта.

    Таким образом сообщения, которыми обмениваются процессы имеют структуру:
        (destination_name, source_name,
        destination_number, source_number,
        data)

    Принимается, что номера портов ниже 1024 используются для определенных
    заранее сервисов. А номера выше 1024 для выбора номеров при запросах.

    Примечание. message_number имеет тип int, то есть максимально мы сможем
    отправить чуть более 4 млрд сообщений.

    Бот поддерживает следующие структуры для обработки входящих сообщений:
    self.listen -- (dict) указывает какие запросы будет обрабатывать бот.
                    Ключами являются номера портов, значения - функции обработки
                    запросов.
    self.waiting --  (dict) содержит список отправленных нами запросов, на
                     которые мы ждем ответ. Ключом является кортеж вида
                     (имя_бота, номер_порта_запроса), значения - функция
                     обработки и дополнительные параметры.
    """
    def __init__(self, name, pipe):
        """
        Устанавливаем общие для всех ботов параметры.

        Аргументы:
           name -- (string) имя бота, используется для коммутации сообщений
           pipe -- (Pipe) канал обмена сообщениями

        Собственные переменные:
           hold -- (bool) флаг переводящий бота в режим ожидания
           message_number -- (int) счетчик сообщений
           listen -- (dict) инструкции по обработке запросов
           requests -- (dict) инструкции по обработке ответов на отправленные
                       нами запросы
           log_time_format -- (string) формат применяемый ко времени
                              в лог-сообщениях
        """
        self.name = name
        self.pipe = pipe
        self.hold = False
        self.message_number = 1025
        self.listen = {}
        self.waiting = {}
        self.log_time_format = ''

        print 'Me alive! Me name:', self.name  # debugging

################################################################################
    #   Логика работы

    def __call__(self):
        """
        Предполагается, что мы будем запускать бота в отдельном процессе/нити.
        """
        self.open_control_port()
        self.configure()
        while True:
            if self.hold:
                self.wait_for_message()
            else:
                self.bot_logic()

    def open_control_port(self):
        self.listen[161] = self.change_state

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
    #   Обмен сообщениями

    def send_msg(self, dest, dest_port, data,
                 reply_needed=False, callback=None, *args):
        """
        Отправляет сообщение.
        Опционально устанавливает, что делать когда получен ответ на сообщение.

        Аргументы:
           dest -- (string) имя процесса, которому отправляется сообщение
           dest_port -- (int) номер порта, на котором расположен интересующий
                        нас обработчик
           data -- (any type) данные, которые будут отправлены
           reply_needed -- (bool) флаг, показывающий ожидать ли
                           ответа на это сообщение
           callback -- (callable) функция, которая будет вызвана, когда будет
                       получен ответ, данные из ответа будут переданы ей
           args -- (iterable) дополнительные аргументы для функции
                   обработки ответа
        """
        if reply_needed:
            assert callback is not None
            self.waiting[(dest, self.message_number)] = (callback, args)
        packet = (dest, self.name, dest_port, self.message_number, data)
        self.pipe.send(packet)
        self.message_number += 1

    def _process_message(self):
        """
        Прочитать и обработать одно сообщение из канала.
        Канал должен содержать хотя бы одно сообщение. Иначе мы тут зависнем,
        а мы этого не хотим. Подождать можно в другом месте.

        Должны существовать инструкции по обратокте этого сообщения, либо в
        self.listen, либо в self.waiting. Иначе оно будет отброшено.
        """
        assert self.pipe.poll()

        dest, source, dest_port, source_port, data = self.pipe.recv()
        assert dest == self.name, \
            " ".join(('Msg for', dest, 'got by', self.name))

        if dest_port in self.listen.keys():
            process = self.listen[dest_port]
            reply = process(data)
            if reply is not None:
                self.send_msg(source, source_port, reply)

        elif (source, dest_port) in self.waiting.keys():
            callback, args = self.waiting[(source, dest_port)]
            callback(data, *args)
            del self.waiting[(source, dest_port)]

    def get_all_messages(self):
        """
        Обрабатывает все сообщения, имеющиеся в канале на данный момент.
        """
        while self.pipe.poll():
            self._process_message()

    def wait_for_message(self, timeout=None):
        """
        Ожидает получения любого сообщения.

        Аргументы:
           timeout -- (int) количество секунд, в течение которых будет ожидаться
                      сообщение. По умолчанию - ожидать бесконечно.
        """
        if self.pipe.poll(timeout):
            self._process_message()

    def wait_all_replies(self):
        """
        Ожидает получения всех ответов на отправленные запросы
        """
        while self.waiting:
            self.wait_for_message()

################################################################################
    #   Изменение состояния

    def change_state(self, data):
        """
        Обработчик команд.
        """
        raise NotImplementedError

################################################################################
#   Дополнительные функции

    def require_attr(self, attr_name, bot_name, bot_port, request, callback):
        """
        Обрабатывает ситауцию необходимости получения значения локального
        аттрибута от другого бота.
        Запрашивает данные, дожадается ответа и устанавливает свой аттрибут
        в определенное значение на основании этих данных

        Аргументы:
           attr_name -- (string) имя аттрибута, который необходимо установить
           bot_name -- (string) имя бота, которому отправить запрос
           bot_port -- (int) порт, на котором находится сервис
           request -- запрос в формате, поддерживаемом ботом-получателем
           callback -- (callable) функция, которая обработает ответ и установит
                        локальный параметр
        """
        setattr(self, attr_name, None)
        self.send_msg(bot_name, bot_port, request, True, callback)
        while getattr(self, attr_name) is None:
            self.wait_for_message()

    def send_log(self, level, message):
        """
        Отправляет сообщение боту logger.

        Аргументы:
           level -- (int) уровень важности сообщения
           message -- (string) текст сообщения
        """
        self.send_msg('log', 514, {'level': level, 'message': message})

    def now(self):
        """
        Возвращает текущую дату и время в определенном ранее формате.
        """
        return time.strftime(self.log_time_format)