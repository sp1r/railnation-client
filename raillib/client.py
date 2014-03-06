#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Подробные структуры ответов сервера находятся в файле DATA_STRUCTS.
Значения id ресурсов, товаров и зданий могут быть найдены в модуле constants.py.
"""
import json
import requests
import requests.exceptions
import hashlib
import time

__author__ = 'V. Spir'


class Engine:
    """
    Настраиваем программу на работу с сервером railnation
    Мы будем выдавать себя за браузер Mozilla Firefox из-под Ubuntu
    """
    def __init__(self, url, cookie, checksum):
        """
        Самое важное это наша кука. Добывается из браузера.
        """
        self.url = url
        self.cookie = cookie
        self.checksum = checksum
        self.session = requests.Session()
        #self.session.params.update({'pool_maxsize': 20, 'max_retries': 20})
        self.session.headers.update({'content-type': 'application/json',
                                    "Cookie": self.cookie,
                                    "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; \
                                    Linux x86_64; rv:26.0) Gecko/20100101 \
                                    Firefox/26.0'})

    def _quote_list(self, l):
        return '[' + ','.join([self._quote(i) for i in l]) + ']'

    def _quote_dict(self, d):
        return '{' + ','.join([self._quote(k) + ':' + self._quote(v) for k, v in d.items()]) + '}'

    def _quote(self, item):
        if type(item) is list:
            return self._quote_list(item)
        if type(item) is dict:
            return self._quote_dict(item)
        elif type(item) is str:
            return '"' + item + '"'
        else:
            return str(item).lower()

    def produce(self, interface, method, params):
        """
        Игра использует обращения к веб-сервису по паре ключей interface+method.
        При этом отсылая и принимая json-пакеты с данными.

        Ответ обычно имеет следующую структуру:
            {"Server":"Apollon V1",
            "Errorcode":0,
            "Infos":{"Server-Time":0.043523788452148},
            "Body":JSON_DATA}
        """
        target = {'interface': interface,
                  'method': method}
        # С какого-то момента сервер хочет от нас в запросе md5-хэш строки
        # параметров.
        params_str = self._quote_list(params)
        payload = {'ckecksum': self.checksum,
                   'client': 1,
                   'hash': hashlib.md5(params_str).hexdigest(),
                   'parameters': params}
        while True:
            try:
                r = self.session.post(self.url,
                                      params=target,
                                      data=json.dumps(payload))
                return json.loads(r.content)  # works in Ubuntu 12.04/Debian 7
                #return json.loads(r.text)  # works in Fedora 19
            except requests.exceptions.ConnectionError:
                # calm down and try again
                #print 'got error, will try again after a second'
                time.sleep(1)


class Oracle:
    """
    Методы, с которыми можно обращаться к серверу собраны тут.
    """
    def __init__(self, engine):
        self.srv = engine

    def get_my_id(self, web_key='42cbf556576ddc85a560ff2d7909c020'):
        """
        Проверяет действительна ли наша кука.
        В случае успеха возвращает id игрока, которому она принадлежит.

        Параметр web_key - чистая условность, может быть любой строкой.
        """
        return self.srv.produce('AccountInterface', 'is_logged_in', [web_key])

    def get_user(self, user_id):
        """
        Возвращает информацию о игроке по его ID.

        Параметры:
        user_id -- id игрока (string)
        """
        return self.srv.produce('ProfileInterface', 'get_profile_data',
                                [user_id])

    def get_corp(self, corp_id):
        """
        Возвращает информацию о корпорации по ее ID

        Параметры:
        corp_id -- id ассоциации (string)
        """
        return self.srv.produce('CorporationInterface', 'get', [corp_id])

    def get_buildings(self, user_id):
        """
        Возвращает информацию о станции игрока по его ID

        Параметры:
        user_id -- id игрока (string)
        """
        return self.srv.produce('BuildingsInterface', 'getAll', [user_id])

    def collect(self, user_id, building_id):
        """
        Собирает бонус со здания игрока своей корпорации (если готов)

        Параметры:
        user_id -- id игрока (string)
        building_id -- номер здания (int)
        """
        return self.srv.produce('BuildingsInterface', 'collect',
                                [building_id, user_id])
    
    def collect_self(self, building_id):
        """
        Собирает бонус со своего здания (если готов)

        Параметры:
        building_id -- номер здания (int)
        """
        return self.srv.produce('BuildingsInterface', 'collect', [building_id])

    def check_lottery(self):
        """
        Проверяет доступен ли бесплатный билетик.
        """
        return self.srv.produce('LotteryInterface', 'isForFree', [])

    def collect_ticket(self):
        """
        Открывает лотерейный билет (покупает его если нет бесплатного)
        """
        print self.srv.produce('LotteryInterface', 'buy', [])
        return self.srv.produce('LotteryInterface', 'rewardLottery', [])

    def build(self, building_id):
        """
        Пытается начать строительство

        Параметры:
        building_id -- номер здания (int)
        """
        return self.srv.produce('BuildingsInterface', 'build',
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
        return self.srv.produce('ResourceInterface', 'getResource',
                                [user_id, resource_id])

    def get_gui(self):
        """
        Этот метод вызывает клиент, сразу после возвращения из режима
        неактивности. Возвращает информацию сразу о всех ресурсах.
        """
        return self.srv.produce('GUIInterface', 'get_gui', [])

    def get_all_tenders(self):
        """
        Возвращает список всех соревнований (прошедших, текущих и будущих)
        """
        return self.srv.produce('TenderingInterface', 'getAllTendering', [])

    def accept_tender(self, comp_id):
        """
        Регистрируется на соревнование

        Параметры:
        comp_id -- id соревнования (string)
        """
        return self.srv.produce('TenderingInterface', 'acceptTendering',
                                [comp_id, False])

    def get_licence_auctions(self):
        """
        Возвращает список всех аукционов на лицензии
        """
        return self.srv.produce('LicenceInterface', 'getAuctions', [])

    def bid_on_licence(self, auc_id, amount):
        """
        Делает ставку на лицензию

        Параметры:
        auc_id -- id аукциона (string)
        amount -- размер ставки (int)
        """
        return self.srv.produce('LicenceInterface', 'bidOnLicence',
                                [auc_id, amount])

    def get_own_licences(self):
        """
        Возвращает список своих лицензий
        """
        return self.srv.produce('LicenceInterface', 'getOwnLicences', [])

    def research(self, tech_id, points):
        """
        Исследует технологию

        Параметры:
        tech_id -- id технологии (int)
        points -- количество очков исследования, которые нужно вложить (int)
        """
        return self.srv.produce('ResearchInterface', 'researchTechnology',
                                [tech_id, points])

    def get_my_trains(self):
        """
        Возвращает список своих поездов
        """
        return self.srv.produce('TrainInterface', 'getMyTrains', [True])

    def get_train(self, train_id):
        """
        Возвращает информацию об одном из поездов

        Параметры:
        train_id -- id поезда (string)
        """
        return self.srv.produce('TrainInterface', 'getTrack',
                                [train_id, True, False])

    def get_train_road_map(self, train_id):
        """
        Возвращает маршрут поезда

        Параметры:
        train_id -- id поезда (string)
        """
        return self.srv.produce('TrainInterface', 'getRoadMap', [train_id])

    def repair_train(self, train_id):
        """
        Ремонтирует поезд

        Параметры:
        train_id -- id поезда (string)
        """
        return self.srv.produce('TrainInterface', 'doMaintenance', [train_id])

    def get_locations(self):
        """
        Возвращает список всех локаций на карте
        """
        return self.srv.produce('LocationInterface', 'get', [])

    def get_rails(self, user_id):
        """
        Возвращает список рельс, принадлежащих игроку

        Параметры:
        user_id -- id игрока (string)
        """
        return self.srv.produce('RailInterface', 'get', [user_id])

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
        return self.srv.produce('TrainInterface', 'setRoadMap',
                                [train_id, road_map])

################################################################################
    # TODO: Write documentation for functions below

    def get_town_resource(self, town_id, res_id):
        return self.srv.produce('TownInterface', 'getTopSuppliers',
                                [town_id, res_id,
                                 "00000000-0000-0000-0000-000000000000"])

    def get_town_brief(self, town_id):
        return self.srv.produce('TownInterface', 'getDetails',
                                [town_id])

    def get_statistics_towns(self):
        return self.srv.produce('StatisticsInterface', 'getTowns', [])

    def get_all_locations(self):
        return self.srv.produce('LocationInterface', 'get', [])