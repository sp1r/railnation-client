#!/usr/bin/python
# -*- coding: utf-8 -*-

author__ = 'spir'

import modules
import modules_config

main_module_name = "root"

################################################################################
# Загружаемые модули

load_modules = [
    ('game', modules.WebClient, modules_config.game.configuration),
    ('logger', modules.FileLogger, modules_config.file_log.configuration),
    ('collect', modules.Stranger, modules_config.collect.configuration)
]

################################################################################
# Архитектура

# Сервисы, которые предоставляются компонентами бота. Могут быть использованы
# другими компонентами. В коде бота, нужно использовать указаный ниже
# краткий алиас.
service = {
    # Name Resolution Service - служит для сопоставления имени сервиса и имени
    # бота предоставляющего этот сервис. Поддерживается головной программой.
    'Name_Resolution': 'name',

    # Server Query - формирует запросы к серверу игры и возвращает ответы.
    'Server_Query': 'query',

    # Logging - принимает информационные сообщения от других ботов и записывает
    # их в лог.
    'Logging': 'log',

    # GUI Monitor - отвечает за отображение статистической информации в
    # графическом представлении.
    'GUI_Monitor': 'monitor',

    # Train Management - отвечает за назначение поездам маршрутов и их ремонт.
    'Train_Management': 'trains',

    # Money Management - отвечает за выделение денег на нужды других ботов.
    'Money_Management': 'money',

    # Research Management - отвечает за выделение очков исследования.
    'Research_Management': 'research',

    # Gold Management - отвечает за выделение золота.
    'Gold_Management': 'gold',
}

# Номера портов, на которых должны работать сервисы, предоставляемые модулями.
service_ports = {
    'query': 80,
    'log': 0,
    'monitor': 0,
    'trains': 0,
    'money': 0,
    'research': 0,
    'gold': 0,
}

