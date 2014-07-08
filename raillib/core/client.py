#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Подробные структуры ответов сервера находятся в файле docs/DATA_STRUCTS.
Значения id ресурсов, товаров и зданий могут быть найдены в модуле constants.py.
"""
import json
import requests
import requests.exceptions
import hashlib
import time

from core.base import (
    config,
    log
)

__author__ = 'sp1r'


class Engine:
    """
    Класс реализующий непосредственное общение с сервером rail-nation.
    """
    def __init__(self, session):
        """
        :param session: Экземпляр requests.Session с пройденной аутентификацией.
        :return: Экземпляр класса, готовый к общению с сервером игры.
        """
        self.url = config['rpc_url'] + '/web/rpc/flash.php'
        self.checksum = config['checksum']
        self.session = session
        #self.session.params.update({'pool_maxsize': 20, 'max_retries': 20})
        self.session.headers.update({'content-type': 'application/json'})

    def _quote(self, item):
        """
        Правильная расстановка кавычек и скобочек в стиле json.

        :param item: объект любого типа
        :return: строка с правильно расставленными кавычками
        """
        if type(item) is list:
            return '[' + ','.join([self._quote(i) for i in item]) + ']'
        elif type(item) is dict:
            return '{' + ','.join([self._quote(k) + ':' + self._quote(v) for k, v in item.items()]) + '}'
        elif type(item) is str:
            return '"' + item + '"'
        else:
            return str(item).lower()

    def produce(self, interface, method, params):
        """
        Обращение к серверу.
        Игра использует обращения к веб-сервису по паре ключей (interface + method).
        При этом отсылая и принимая json-кодированные данные.

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
        params_str = self._quote(params)
        payload = {'ckecksum': self.checksum,
                   'client': 1,
                   'hash': hashlib.md5(params_str.encode("utf-8")).hexdigest(),
                   'parameters': params}
        while True:
            try:
                r = self.session.post(self.url,
                                      params=target,
                                      data=json.dumps(payload))
                log.debug('Response: %s Error: %s Content: %s' % (r.status_code, r.error, r.text))
                return json.loads(r.text)  # works in Ubuntu 12.04/Debian 7
                #return json.loads(r.text)  # works in Fedora 19
            except requests.exceptions.ConnectionError:
                # calm down and try again
                log.error('Got connection error, will try again after a second')
                time.sleep(1)


class Client:
    """
    Уровень абстракции для общения с игрой.
    Продоставляет доступ к игровой информации.
    """
    def __init__(self):
        #self.authorized = False
        self.engine = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0'})

    def authorize(self):
        self.engine = Engine(self.session)
        config['self_id'] = self.get_my_id(config['web_key'])['Body']
        if config['self_id']:
            self.get_properties()
            #self.authorized = True

    def unauthorize(self):
        self.engine = None
        #self.authorized = False

    def produce(self, *args):
        # if self.authorized:
        #     return self.engine.produce(*args)
        # else:
        #     print("Unauthorized!")
        #     return None
        return self.engine.produce(*args)

########################################################################################################################
    # Standard Library Methods

    def get_properties(self):
        """
        Загружает свойства.
        """
        return self.produce('PropertiesInterface', 'getData', [])

    def get_my_id(self, web_key='42cbf556576ddc85a560ff2d7909c020'):
        """
        Проверяет действительна ли наша кука.
        В случае успеха возвращает id игрока, которому она принадлежит.
        """
        return self.produce('AccountInterface', 'is_logged_in', [web_key])

    def get_user(self, user_id):
        """
        Возвращает информацию о игроке по его ID.

        Параметры:
        user_id -- id игрока (string)
        """
        return self.produce('ProfileInterface', 'get_profile_data',
                            [user_id])

    def get_corp(self, corp_id):
        """
        Возвращает информацию о корпорации по ее ID

        Параметры:
        corp_id -- id ассоциации (string)
        """
        return self.produce('CorporationInterface', 'get', [corp_id])

    def get_buildings(self, user_id):
        """
        Возвращает информацию о станции игрока по его ID

        Параметры:
        user_id -- id игрока (string)
        """
        return self.produce('BuildingsInterface', 'getAll', [user_id])

    def collect(self, user_id, building_id):
        """
        Собирает бонус со здания игрока своей корпорации (если готов)

        Параметры:
        user_id -- id игрока (string)
        building_id -- номер здания (int)
        """
        return self.produce('BuildingsInterface', 'collect',
                                [building_id, user_id])

    def collect_self(self, building_id):
        """
        Собирает бонус со своего здания (если готов)

        Параметры:
        building_id -- номер здания (int)
        """
        return self.produce('BuildingsInterface', 'collect', [building_id])

    def check_lottery(self):
        """
        Проверяет доступен ли бесплатный билетик.
        """
        return self.produce('LotteryInterface', 'isForFree', [])

    def collect_ticket(self):
        """
        Открывает лотерейный билет (покупает его если нет бесплатного)
        """
        print(self.produce('LotteryInterface', 'buy', []))
        return self.produce('LotteryInterface', 'rewardLottery', [])

    def build(self, building_id):
        """
        Пытается начать строительство

        Параметры:
        building_id -- номер здания (int)
        """
        return self.produce('BuildingsInterface', 'build',
                                [building_id, False, False])

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
        return self.produce('ResourceInterface', 'getResource',
                                [user_id, resource_id])

    def get_gui(self):
        """
        Этот метод вызывает клиент, сразу после возвращения из режима
        неактивности. Возвращает информацию сразу о всех ресурсах.
        """
        return self.produce('GUIInterface', 'get_gui', [])

    def get_all_tenders(self):
        """
        Возвращает список всех соревнований (прошедших, текущих и будущих)
        """
        return self.produce('TenderingInterface', 'getAllTendering', [])

    def accept_tender(self, comp_id):
        """
        Регистрируется на соревнование

        Параметры:
        comp_id -- id соревнования (string)
        """
        return self.produce('TenderingInterface', 'acceptTendering',
                                [comp_id, False])

    def get_licence_auctions(self):
        """
        Возвращает список всех аукционов на лицензии
        """
        return self.produce('LicenceInterface', 'getAuctions', [])

    def bid_on_licence(self, auc_id, amount):
        """
        Делает ставку на лицензию

        Параметры:
        auc_id -- id аукциона (string)
        amount -- размер ставки (int)
        """
        return self.produce('LicenceInterface', 'bidOnLicence',
                                [auc_id, amount])

    def get_own_licences(self):
        """
        Возвращает список своих лицензий
        """
        return self.produce('LicenceInterface', 'getOwnLicences', [])

    def research(self, tech_id, points):
        """
        Исследует технологию

        Параметры:
        tech_id -- id технологии (int)
        points -- количество очков исследования, которые нужно вложить (int)
        """
        return self.produce('ResearchInterface', 'researchTechnology',
                                [tech_id, points])

    def get_my_trains(self):
        """
        Возвращает список своих поездов
        """
        return self.produce('TrainInterface', 'getMyTrains', [True])

    def get_train(self, train_id):
        """
        Возвращает информацию об одном из поездов

        Параметры:
        train_id -- id поезда (string)
        """
        return self.produce('TrainInterface', 'getTrack',
                                [train_id, True, False])

    def repair_train(self, train_id):
        """
        Ремонтирует поезд

        Параметры:
        train_id -- id поезда (string)
        """
        return self.produce('TrainInterface', 'doMaintenance', [train_id])

    def get_locations(self):
        """
        Возвращает список всех локаций на карте
        """
        return self.produce('LocationInterface', 'get', [])

    def get_rails(self, user_id):
        """
        Возвращает список рельс, принадлежащих игроку

        Параметры:
        user_id -- id игрока (string)
        """
        return self.produce('RailInterface', 'get', [user_id])

    def get_train_road_map(self, train_id):
        """
        Возвращает маршрут поезда

        Параметры:
        train_id -- id поезда (string)
        """
        return self.produce('TrainInterface', 'getRoadMap', [train_id])

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
        return self.produce('TrainInterface', 'setRoadMap',
                                [train_id, road_map])

################################################################################
    # TODO: Write documentation for functions below

    def get_town_resource(self, town_id, res_id):
        return self.produce('TownInterface', 'getTopSuppliers',
                                [town_id, res_id,
                                 "00000000-0000-0000-0000-000000000000"])

    def get_town_brief(self, town_id):
        return self.produce('TownInterface', 'getDetails',
                                [town_id])

    def get_statistics_towns(self):
        return self.produce('StatisticsInterface', 'getTowns', [])

    def get_all_locations(self):
        return self.produce('LocationInterface', 'get', [])