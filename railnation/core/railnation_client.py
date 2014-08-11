# -*- coding: utf-8 -*-
"""
Классы предоставляющие доступ к игровой информации на сервере.

Список всех методов с описанием см в docs/game_methods

Примеры ответов сервера находятся в файле docs/server_answers_examples.
"""
import json
import requests
import requests.exceptions
import hashlib
import time
import sys

from railnation.models.model_player import Player
from railnation.models.model_corporation import Corporation
from railnation.models.model_station import Station


CLIENT_CHECKSUM = 'ea24d4af2c566004782f750f940615e5'  # hardcoded in flash-app
ZERO_UUID = '00000000-0000-0000-0000-000000000000'
MAX_RECONNECT = 10


class Engine:
    """Непосредственное общение с сервером rail-nation"""
    def __init__(self, session, log):
        self.checksum = CLIENT_CHECKSUM
        self.rpc_url = ''
        self.session = session
        self.log = log

    def produce(self, interface, method, params):
        """
        Обращение к серверу.

        :param interface: имя интерфейса
        :type interface: str
        :param method: имя метода
        :type method: str
        :param params: параметры вызова
        :type params: list
        :return: ответ сервера
        :rtype: dict
        """
        self.log.debug('Trying: %s %s %s' % (interface, method, params))
        target = {'interface': interface,
                  'method': method}
        payload = {'ckecksum': self.checksum,
                   'client': 1,
                   'hash': _make_hash(params),
                   'parameters': params}

        connect = 0
        while connect < MAX_RECONNECT:
            connect += 1
            try:
                r = self.session.post(self.rpc_url,
                                      params=target,
                                      data=json.dumps(payload),
                                      timeout=1)

            except requests.exceptions.ConnectionError:
                self.log.warning('Connection problems.')
                time.sleep(1)

            except requests.exceptions.Timeout:
                self.log.warning('No response from server (timeout).')

            # если нет ошибок - возвращаем ответ
            else:
                self.log.debug('Response: %s Error: %s Content: %s' %
                          (r.status_code, r.reason, r.content))
                return r.json

        # более чем 10 неудачных попыток соединения считаем критической
        # ошибкой и выходим
        else:
            self.log.critical('Too much connection errors. Will now exit.')
            sys.exit(1)


class Client:
    """
    Уровень абстракции для общения с игрой.

    Заменяет используемые в игре пары Interface_name+Method_name на
    короткие человеческие имена. И работает с классами из railnation.models,
    где возможно.
    """
    def __init__(self, session, log):
        self.log = log
        self.engine = Engine(session, log)
        self.webkey = ''
        self.player_id = ''

    def is_logged_in(self):
        self.player_id = self.get_my_id()
        if self.player_id == 'False':
            return False
        else:
            return True

    def get_myself(self):
        return self.get_user(self.player_id)

    # ##########################################################################
    # Properties
    ############################################################################
    def get_properties(self):
        """
        Загружает свойства игры.

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('PropertiesInterface', 'getData', [])

    ############################################################################
    # Account
    ############################################################################
    def get_my_id(self):
        """
        Проверяет действительна ли наша кука.
        В случае успеха возвращает id игрока, которому она принадлежит.
        В случае неудачи возвращает 'Body': False

        :return: ответ сервера
        :rtype: str or bool
        """
        return str(self.engine.produce('AccountInterface', 'is_logged_in',
                                   [self.webkey])['Body'])

    ############################################################################
    # Profile
    ############################################################################
    def get_user(self, user_id):
        """
        Возвращает игрока по его ID.

        :param user_id: id игрока
        :type user_id: str
        :return: игрок
        :rtype: Player
        """
        return Player(self.engine.produce('ProfileInterface',
                                          'get_profile_data',
                                          [user_id])['Body'])

    ############################################################################
    # Corporation
    ############################################################################
    def get_corp(self, corp_id):
        """
        Возвращает корпорацию по ее ID

        :param corp_id: id ассоциации
        :type corp_id: str
        :return: корпорация
        :rtype: Corporation
        """
        return Corporation(self.engine.produce('CorporationInterface', 'get',
                                   [corp_id])['Body'])

    ############################################################################
    # Buildings
    ############################################################################
    def get_station(self, user_id):
        """
        Возвращает информацию о станции игрока по его ID

        :param user_id: id игрока
        :type user_id: str
        :return: станция
        :rtype: Station
        """
        return Station(user_id, self.engine.produce('BuildingsInterface',
                                                    'getAll',
                                                    [user_id])['Body'])

    def collect(self, user_id, building_id):
        """
        Собирает бонус со здания игрока своей корпорации (если готов)

        :param user_id: id игрока
        :type user_id: str
        :param building_id: номер здания
        :type building_id: int
        :return: ответ сервера
        :rtype: dict
        """
        if user_id == self.player_id:
            return self.engine.produce('BuildingsInterface', 'collect',
                                       [building_id])
        else:
            return self.engine.produce('BuildingsInterface', 'collect',
                                       [building_id, user_id])

    def build(self, building_id):
        """
        Пытается начать строительство

        :param building_id: номер здания
        :type building_id: int
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('BuildingsInterface', 'build',
                                   [building_id, False, False])

    ############################################################################
    # Lottery
    ############################################################################
    def check_lottery(self):
        """
        Проверяет доступен ли бесплатный билетик.

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('LotteryInterface', 'isForFree', [])

    def collect_ticket(self):
        """
        Открывает лотерейный билет (покупает его если нет бесплатного)

        :return: ответ сервера
        :rtype: dict
        """
        print(self.engine.produce('LotteryInterface', 'buy', []))
        return self.engine.produce('LotteryInterface', 'rewardLottery', [])

    ############################################################################
    # Resources
    ############################################################################
    def get_resource(self, user_id, resource_id):
        """
        Возвращает количество определенного ресурса у игрока (любого!)

        :param user_id: id игрока
        :type user_id: str
        :param resource_id: номер ресурса
        :type resource_id: int
        :return: ответ сервера
        :rtype: dict

        Примечание:
        этот метод не используется клиентом игры, может быть лучше его не
        трогать?
        """
        return self.engine.produce('ResourceInterface', 'getResource',
                                   [user_id, resource_id])

    ############################################################################
    # GUI
    ############################################################################
    def get_gui(self):
        """
        Этот метод вызывает клиент, сразу после возвращения из режима
        неактивности. Возвращает информацию сразу о всех ресурсах.

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('GUIInterface', 'get_gui', [])

    ############################################################################
    # Tendering
    ############################################################################
    def get_all_tenders(self):
        """
        Возвращает список всех соревнований (прошедших, текущих и будущих)

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TenderingInterface', 'getAllTendering', [])

    def accept_tender(self, tendering_id):
        """
        Регистрируется на соревнование

        :param tendering_id: id соревнования
        :type tendering_id: str
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TenderingInterface', 'acceptTendering',
                                   [tendering_id, False])

    ############################################################################
    # Licence
    ############################################################################
    def get_licence_auctions(self):
        """
        Возвращает список всех аукционов на лицензии

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('LicenceInterface', 'getAuctions', [])

    def bid_on_licence(self, auction_id, amount):
        """
        Делает ставку на лицензию

        :param auction_id: id аукциона
        :type auction_id: str
        :param amount: количество денег
        :type amount: int
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('LicenceInterface', 'bidOnLicence',
                                   [auction_id, amount])

    def get_own_licences(self):
        """
        Возвращает список своих лицензий

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('LicenceInterface', 'getOwnLicences', [])

    ############################################################################
    # Research
    ############################################################################
    def research(self, tech_id, points):
        """
        Исследует технологию

        :param tech_id: id технологии
        :type tech_id: str
        :param points: количество очков исследования
        :type points: int
        :return: ответ сервера
        :rtype: dict

        Внимание: если ошибешься в id технологии - очки пропадут бесследно!
        """
        return self.engine.produce('ResearchInterface', 'researchTechnology',
                                   [tech_id, points])

    ############################################################################
    # Train
    ############################################################################
    def get_my_trains(self):
        """
        Возвращает список своих поездов

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TrainInterface', 'getMyTrains',
                                   [True])

    def get_train(self, train_id):
        """
        Возвращает информацию об одном из поездов

        :param train_id: id поезда
        :type train_id: str
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TrainInterface', 'getTrack',
                                   [train_id, True, False])

    def repair_train(self, train_id):
        """
        Ремонтирует поезд

        :param train_id: id поезда
        :type train_id: str
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TrainInterface', 'doMaintenance',
                                   [train_id])

    def get_train_road_map(self, train_id):
        """
        Возвращает маршрут поезда

        :param train_id: id поезда
        :type train_id: str
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TrainInterface', 'getRoadMap',
                                   [train_id])

    def set_train_road_map(self, train_id, road_map):
        """
        Устанавливает маршрут для указанного поезда

        :param train_id: id поезда
        :type train_id: str
        :param road_map: маршрут
        :type road_map: list
        :return: ответ сервера
        :rtype: dict

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

    ############################################################################
    # Location
    ############################################################################
    def get_locations(self):
        """
        Возвращает список всех локаций на карте

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('LocationInterface', 'get', [])

    ############################################################################
    # Rail
    ############################################################################
    def get_rails(self, user_id):
        """
        Возвращает список рельс, принадлежащих игроку

        :param user_id: id игрока
        :type user_id: str
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('RailInterface', 'get',
                                   [user_id])

    ############################################################################
    # Town
    ############################################################################
    def get_town_suppliers(self, town_id, res_id):
        """
        Полный список поставщиков ресурса в городе.

        :param town_id: id города
        :type town_id: str
        :param res_id: номер ресурса
        :type res_id: int
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TownInterface', 'getTopSuppliers',
                                   [town_id, res_id,
                                    "00000000-0000-0000-0000-000000000000"])

    def get_town_details(self, town_id):
        """
        Информация о городе.

        :param town_id: id города
        :type town_id: str
        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('TownInterface', 'getDetails',
                                   [town_id])

    ############################################################################
    # Statistics
    ############################################################################
    def get_statistics_towns(self):
        """
        Рейтинг городов.

        :return: ответ сервера
        :rtype: dict
        """
        return self.engine.produce('StatisticsInterface', 'getTowns', [])


def _quote(item):
    """
    Правильная расстановка кавычек и скобочек в стиле json.
    Необходима для того, чтобы md5-сумма строки параметров вычислялась
    правильно.

    :param item: объект любого типа
    :type item: str or dict or list of bool or int
    :return: строка с правильно расставленными кавычками
    :rtype: str
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
    """Сокращение"""
    return hashlib.md5(_quote(item).encode("utf-8")).hexdigest()