#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Классы предоставляющие доступ к игровой информации на сервере.

Список всех методов с описанием см в docs/game_methods

Примеры ответов сервера находятся в файле docs/DATA_STRUCTS.
Значения id ресурсов, товаров и зданий могут быть найдены в raillib.constants
"""
import json
import requests
import requests.exceptions
import hashlib
import time
import sys

from . import log
from . import config
from . import session


__author__ = 'sp1r'


log.info('Client module Initialization...')


def _quote(item):
    """
    Правильная расстановка кавычек и скобочек в стиле json.
    Необходима для того, чтобы md5-сумма от параметров считалась
    правильно.

    :param item: объект любого типа
    :return: строка с правильно расставленными кавычками
    """
    if isinstance(item, list):
        return '[' + ','.join([_quote(i) for i in item]) + ']'
    elif isinstance(item, dict):
        return '{' + ','.join([_quote(k) + ':' + _quote(v)
                              for k, v in item.items()]) + '}'
    elif isinstance(item, str):
        return '"' + item + '"'
    else:
        return str(item).lower()


def _make_hash(item):
    """Сокращение записи"""
    return hashlib.md5(_quote(item).encode("utf-8")).hexdigest()


class Engine:
    """
    Класс реализующий непосредственное общение с сервером rail-nation.
    """
    def __init__(self):
        """
        :return: Экземпляр класса, готовый к общению с сервером игры.
        """
        self.checksum = config['checksum']
        self.session = session

    def produce(self, interface, method, params):
        """
        Обращение к серверу.

        Ответ имеет следующую структуру:
            {"Server": "Apollon V1",
            "Errorcode": 0,
            "Infos": {"Server-Time": 0.043523788452148},
            "Body": JSON_DATA}

        :param interface: имя интерфейса (string)
        :param method: имя метода (string)
        :param params: параметры вызова (list)
        :return: ответ сервера (dict)
        """
        log.debug('Trying: %s %s %s' % (interface, method, params))
        target = {'interface': interface,
                  'method': method}
        log.debug('    target = %s' % str(target))
        payload = {'ckecksum': self.checksum,
                   'client': 1,
                   'hash': _make_hash(params),
                   'parameters': params}
        log.debug('    payload = %s' % str(payload))

        connect = 0
        max_connects = 10
        while connect < max_connects:
            connect += 1
            try:
                r = self.session.post(config['rpc_url'],
                                      params=target,
                                      data=json.dumps(payload),
                                      headers={'content-type':
                                               'application/json'},
                                      timeout=1)

            except requests.exceptions.ConnectionError:
                log.warning('Connection problems.')
                time.sleep(1)

            except requests.exceptions.Timeout:
                log.warning('No response from server (timeout).')

            # если нет ошибок - возвращаем ответ
            else:
                log.debug('Response: %s Error: %s Content: %s' %
                          (r.status_code, r.error, r.text))
                return json.loads(r.text)

        # более чем 10 неудачных попыток соединения считаем критической
        # ошибкой
        else:
            log.critical('Too much connection errors. Will now exit.')
            sys.exit(1)


class Client:
    """
    Уровень абстракции для общения с игрой.

    Заменяет используемые в игре пары Interface_name+Method_name на
    короткие человеческие имена.
    """
    def __init__(self):
        self.engine = Engine()

###############################################################################
# Properties
###############################################################################
    def get_properties(self):
        """
        Загружает свойства игры.
        """
        return self.engine.produce('PropertiesInterface', 'getData',
                                   [])

###############################################################################
# Account
###############################################################################
    def get_my_id(self, web_key='42cbf556576ddc85a560ff2d7909c020'):
        """
        Проверяет действительна ли наша кука.
        В случае успеха возвращает id игрока, которому она принадлежит.
        В случае неудачи возвращает 'Body': False
        """
        return self.engine.produce('AccountInterface', 'is_logged_in',
                                   [web_key])

###############################################################################
# Profile
###############################################################################
    def get_user(self, user_id):
        """
        Возвращает информацию о игроке по его ID.

        Параметры:
        user_id -- id игрока (string)
        """
        return self.engine.produce('ProfileInterface', 'get_profile_data',
                                   [user_id])

###############################################################################
# Corporation
###############################################################################
    def get_corp(self, corp_id):
        """
        Возвращает информацию о корпорации по ее ID

        Параметры:
        corp_id -- id ассоциации (string)
        """
        return self.engine.produce('CorporationInterface', 'get',
                                   [corp_id])

###############################################################################
# Buildings
###############################################################################
    def get_buildings(self, user_id):
        """
        Возвращает информацию о станции игрока по его ID

        Параметры:
        user_id -- id игрока (string)
        """
        return self.engine.produce('BuildingsInterface', 'getAll',
                                   [user_id])

    def collect(self, user_id, building_id):
        """
        Собирает бонус со здания игрока своей корпорации (если готов)

        Параметры:
        user_id -- id игрока (string)
        building_id -- номер здания (int)
        """
        if user_id == config['cache']['self_id']:
            return self.engine.produce('BuildingsInterface', 'collect',
                                       [building_id])
        else:
            return self.engine.produce('BuildingsInterface', 'collect',
                                       [building_id, user_id])

    def build(self, building_id):
        """
        Пытается начать строительство

        Параметры:
        building_id -- номер здания (int)
        """
        return self.engine.produce('BuildingsInterface', 'build',
                                   [building_id, False, False])

###############################################################################
# Lottery
###############################################################################
    def check_lottery(self):
        """
        Проверяет доступен ли бесплатный билетик.
        """
        return self.engine.produce('LotteryInterface', 'isForFree', [])

    def collect_ticket(self):
        """
        Открывает лотерейный билет (покупает его если нет бесплатного)
        """
        print(self.engine.produce('LotteryInterface', 'buy', []))
        return self.engine.produce('LotteryInterface', 'rewardLottery', [])

###############################################################################
# Resources
###############################################################################
    def get_resource(self, user_id, resource_id):
        """
        Возвращает количество определенного ресурса у игрока (любого!)

        Параметры:
        user_id -- id игрока (string)
        resource_id -- номер ресурса (int)

        Примечание:
        этот метод не используется клиентом игры, может быть лучше его не
        использовать?
        """
        return self.engine.produce('ResourceInterface', 'getResource',
                                   [user_id, resource_id])

###############################################################################
# GUI
###############################################################################
    def get_gui(self):
        """
        Этот метод вызывает клиент, сразу после возвращения из режима
        неактивности. Возвращает информацию сразу о всех ресурсах.
        """
        return self.engine.produce('GUIInterface', 'get_gui', [])

###############################################################################
# Tendering
###############################################################################
    def get_all_tenders(self):
        """
        Возвращает список всех соревнований (прошедших, текущих и будущих)
        """
        return self.engine.produce('TenderingInterface', 'getAllTendering', [])

    def accept_tender(self, comp_id):
        """
        Регистрируется на соревнование

        Параметры:
        comp_id -- id соревнования (string)
        """
        return self.engine.produce('TenderingInterface', 'acceptTendering',
                                   [comp_id, False])

###############################################################################
# Licence
###############################################################################
    def get_licence_auctions(self):
        """
        Возвращает список всех аукционов на лицензии
        """
        return self.engine.produce('LicenceInterface', 'getAuctions',
                                   [])

    def bid_on_licence(self, auc_id, amount):
        """
        Делает ставку на лицензию

        Параметры:
        auc_id -- id аукциона (string)
        amount -- размер ставки (int)
        """
        return self.engine.produce('LicenceInterface', 'bidOnLicence',
                                   [auc_id, amount])

    def get_own_licences(self):
        """
        Возвращает список своих лицензий
        """
        return self.engine.produce('LicenceInterface', 'getOwnLicences',
                                   [])

###############################################################################
# Research
###############################################################################
    def research(self, tech_id, points):
        """
        Исследует технологию

        Параметры:
        tech_id -- id технологии (int)
        points -- количество очков исследования, которые нужно вложить (int)
        """
        return self.engine.produce('ResearchInterface', 'researchTechnology',
                                   [tech_id, points])

###############################################################################
# Train
###############################################################################
    def get_my_trains(self):
        """
        Возвращает список своих поездов
        """
        return self.engine.produce('TrainInterface', 'getMyTrains',
                                   [True])

    def get_train(self, train_id):
        """
        Возвращает информацию об одном из поездов

        Параметры:
        train_id -- id поезда (string)
        """
        return self.engine.produce('TrainInterface', 'getTrack',
                                   [train_id, True, False])

    def repair_train(self, train_id):
        """
        Ремонтирует поезд

        Параметры:
        train_id -- id поезда (string)
        """
        return self.engine.produce('TrainInterface', 'doMaintenance',
                                   [train_id])

    def get_train_road_map(self, train_id):
        """
        Возвращает маршрут поезда

        Параметры:
        train_id -- id поезда (string)
        """
        return self.engine.produce('TrainInterface', 'getRoadMap',
                                   [train_id])

    def set_road_map(self, train_id, road_map):
        """
        Устанавливает маршрут для указанного поезда

        Параметры:
        train_id -- id поезда (string)
        road_map -- массив элементов вида:
             {dest_id: "88a2d6dd-e59c-495b-95e6-bb49845baf5f",
             loading: [{load: 13, type: 4, unload: 0}],
             scheduleType: 1,
             wait: 60},
           где:
             dest_id -- id следующей локации (string)
             loading -- загрузка и разгрузка (не на каждой локации)
             scheduleType -- 1, если этот отрезок входит в периодичекий маршрут
                             2, если этот отрезок нужен, чтобы добраться до
                                периодического маршрута
             wait -- -1, для проходных локаций
                     0, для разгрузки
                     60, для погрузки
        """
        return self.engine.produce('TrainInterface', 'setRoadMap',
                                   [train_id, road_map])

###############################################################################
# Location
###############################################################################
    def get_locations(self):
        """
        Возвращает список всех локаций на карте
        """
        return self.engine.produce('LocationInterface', 'get',
                                   [])

###############################################################################
# Rail
###############################################################################
    def get_rails(self, user_id):
        """
        Возвращает список рельс, принадлежащих игроку

        Параметры:
        user_id -- id игрока (string)
        """
        return self.engine.produce('RailInterface', 'get',
                                   [user_id])

###############################################################################
# Town
###############################################################################
    def get_town_resource(self, town_id, res_id):
        """
        Полный список поставщиков ресурса в городе.

        :param town_id: id города
        :param res_id: id ресурса
        :return: ответ сервера
        """
        return self.engine.produce('TownInterface', 'getTopSuppliers',
                                   [town_id, res_id,
                                   "00000000-0000-0000-0000-000000000000"])

    def get_town_brief(self, town_id):
        """
        Информация о городе.

        :param town_id: id города
        :return: ответ сервера
        """
        return self.engine.produce('TownInterface', 'getDetails',
                                   [town_id])

###############################################################################
# Statistics
###############################################################################
    def get_statistics_towns(self):
        """
        Рейтинг городов.

        :return: ответ сервера
        """
        return self.engine.produce('StatisticsInterface', 'getTowns',
                                   [])
