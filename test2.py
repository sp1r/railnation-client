#!/usr/bin/python
# -*- coding: utf-8 -*-

import raillib
import time
import utils
import shelve
import requests
import json
from modules import Monitor
import multiprocessing as mp

__author__ = 'spir'


# s6
URL = "http://s6.railnation.ru/web/rpc/flash.php"
COOKIE = "PHPSESSID=bla-bla-bla"  # s6
CHECKSUM = "3caf8214532b258daf0118304972727e"  # s6

CONN = (URL, COOKIE, CHECKSUM)

game = raillib.Oracle(raillib.Engine(CONN))

# Me - 3d4151da-515b-a98a-5d2f-b8b2627b6081
# Falcon - 1693e387-b36e-4768-93a9-33883b80be42
# City - 318d7429-1c80-4e10-b93d-abca948def4b
# windows - 784bf6d8-1e59-4ee3-8041-d35b2cb3708c
# wheat - 0e03e417-7601-48e1-88d9-c90276d003b3
# cows - cccea4c6-68e0-422d-a572-e3649953808a

#print game.collect("2d500ea0-dd75-42ae-48e6-b4e821a2ca81", 11)
#print game.is_logged_in("de56462b-56d1-f3d3-1b2b-af6caab28c4b")

#a = game.get_my_trains()
#trains = {}
#for item in a['Body']:
#    tid = item['ID']
#    trains[tid] = {}
#    trains[tid]['type'] = item['type']
#    print tid, trains[tid]['type']

# t = game.get_train('1693e387-b36e-4768-93a9-33883b80be42')
# print t

# p = shelve.open('test.persist')
#
# #locs = game.get_locations()['Body']
# locs = p['body']
# cities = []
# count = 0
# for l in locs:
#     if type(l['name']) is int:
#         cities.append(l['ID'])
#         count += 1
#
# for l in locs:
#     if not type(l['name']) is int:
#         if l['city_location_id'] in cities:
#             print 'found!'
#         else:
#             print "not found ..."
#         count += 1
#
# print count, 'lines'
#
# p.close()

# m = game.get_rails('3d4151da-515b-a98a-5d2f-b8b2627b6081')['Body']
# print 'rails count:', len(m)
#
# road_map = utils.SymbolGraph(len(m))
#
# for x in m:
#     #print x
#     road_map.add_edge(x['location_id1'], x['location_id2'])
#
# for n in road_map.neighbours(road_map.map['318d7429-1c80-4e10-b93d-abca948def4b']):
#     print road_map.keys[n]
#
# print 'root point:', road_map.map['318d7429-1c80-4e10-b93d-abca948def4b']
#
# way_finder = utils.BreadthSearch(road_map,
#                           road_map.map['318d7429-1c80-4e10-b93d-abca948def4b'])
#
# main_way = way_finder.path_to(road_map.map["cccea4c6-68e0-422d-a572-e3649953808a"])
# sec_way = main_way[::-1]
#
# from_loc = '318d7429-1c80-4e10-b93d-abca948def4b'
# to_loc = "cccea4c6-68e0-422d-a572-e3649953808a"
# good_type = 2
# waggons = 6
#
# sched = []
#
# for x in sec_way[:-1]:
#     d = {"dest_id": x,
#          "wait": -1,
#          "loading": [],
#          "scheduleType": 2}
#     sched.append(d)
#     print road_map.keys[x]
#
# x = sec_way.pop()
# d = {"scheduleType": 1,
#      "wait": 60,
#      "loading": [{"load": waggons, "type": good_type, "unload": 0}],
#      "dest_id": x}
# sched.append(d)
#
#
#
#
# # "parameters":["07e539a0-4e99-4c08-8a64-7b328622c5a2",
# # [
# # {"scheduleType":1,"wait":0,"loading":[{"load":7,"type":19,"unload":0}],"dest_id":"a3f27457-3ebc-4db4-bf5d-d287f2709b85"},
# # {"scheduleType":1,"wait":0,"loading":[{"load":0,"type":19,"unload":7}],"dest_id":"64a973fa-20dc-49e3-a8d4-7953f15de533"}
# # ]],
#
# # {"hash":"81367b297ff24884112aa306486d4f47",
# # "checksum":"3caf8214532b258daf0118304972727e",
# # "parameters":["1693e387-b36e-4768-93a9-33883b80be42",[
# # {"scheduleType":2,"wait":-1,"loading":[],"dest_id":"318d7429-1c80-4e10-b93d-abca948def4b"},
# # {"scheduleType":1,"wait":60,"loading":[{"load":6,"type":2,"unload":0}],"dest_id":"0e03e417-7601-48e1-88d9-c90276d003b3"},
# # {"scheduleType":1,"wait":0,"loading":[{"load":0,"type":2,"unload":6}],"dest_id":"318d7429-1c80-4e10-b93d-abca948def4b"}]],
# # "client":1}
#
# # {"hash":"67d4b39cd77b73e05c11c7a5a451ade9",
# # "checksum":"3caf8214532b258daf0118304972727e",
# # "parameters":["1693e387-b36e-4768-93a9-33883b80be42",
# # [
# # {"wait":-1,"dest_id":"318d7429-1c80-4e10-b93d-abca948def4b","loading":[],"scheduleType":2},
# # {"wait":-1,"dest_id":"0e03e417-7601-48e1-88d9-c90276d003b3","loading":[],"scheduleType":2},
# # {"wait":60,"dest_id":"cccea4c6-68e0-422d-a572-e3649953808a","loading":[{"load":6,"type":9,"unload":0}],"scheduleType":1},
# # {"wait":-1,"dest_id":"0e03e417-7601-48e1-88d9-c90276d003b3","loading":[],"scheduleType":1},
# # {"wait":0,"dest_id":"318d7429-1c80-4e10-b93d-abca948def4b","loading":[{"load":0,"type":9,"unload":6}],"scheduleType":1},
# # {"wait":-1,"dest_id":"0e03e417-7601-48e1-88d9-c90276d003b3","loading":[],"scheduleType":1}]],"client":1}
#
# train_id = "1693e387-b36e-4768-93a9-33883b80be42"
#
# d = {"scheduleType": 2, "wait": -1,
#      "loading": [],
#      "dest_id":"318d7429-1c80-4e10-b93d-abca948def4b"}
# sched.append(d)
# d = {"scheduleType": 1, "wait": 60,
#      "loading": [{"load": 6, "type": 2, "unload": 0}],
#      "dest_id":"0e03e417-7601-48e1-88d9-c90276d003b3"}
# sched.append(d)
# d = {"scheduleType": 1, "wait": 0,
#      "loading": [{"load": 0, "type": 2, "unload": 6}],
#      "dest_id":"318d7429-1c80-4e10-b93d-abca948def4b"}
# sched.append(d)
#
# #print sched
#
# print game.set_road_map(train_id, sched)

# for x in sched:
#     print x
#
# y = raillib.Engine(CONN)
# print y._quote_dict(d)

if __name__ == '__main__':
    print game.get_town_brief("318d7429-1c80-4e10-b93d-abca948def4b")
    # name = 33
    # while True:
    #     t = game.get_town_brief("318d7429-1c80-4e10-b93d-abca948def4b") # нью
    #     #t = game.get_town_brief("ef07f109-81bc-4f04-a185-7048a64fa984") # рокс
    #     p = game.get_statistics_towns()
    #     new_vasuki = {}
    #     for town in p['Body']:
    #         if town['name'] == "33":
    #             new_vasuki = town
    #             break
    #     print time.strftime('%H:%M:%S'), \
    #         t['Body']['town']['level'], \
    #         new_vasuki['depots'],
    #     for x in t['Body']['resources']:
    #         if x['priority'] == 1:
    #             print round(x['consume_amount']*1.0/x['amount'], 5),
    #     print
    #     time.sleep(10)
    # url = "http://s6.railnation.ru/web/rpc/flash.php"
    # login_url = 'https://railnation-sam.traviangames.com//iframe/login/consumer/railnation-ru-meta/applicationLanguage/ru-RU'
    # login_target = {'className': 'login',
    #                 'email': 'namelessorama@gmail.com',
    #                 'password': '...',
    #                 'remember_me': '0',
    #                 'submit': 'Вход'}
    # checksum = "ccbd86f54255ab2649ce1a8fededb44a"
    # session = requests.Session()
    # session.params.update({'pool_maxsize': 20, 'max_retries': 10})
    # session.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #                         'Accept-Encoding': 'gzip, deflate',
    #                         'Accept-Language': 'en-US, en; q=0.5',
    #                         'Connection': 'keep-alive',
    #                         'content-type': 'application/x-www-form-urlencoded',
    #                         "Cookie": "_ym_visorc_22363723=b",
    #                         "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; \
    #                                 Linux x86_64; rv:26.0) Gecko/20100101 \
    #                                 Firefox/26.0'})
    #
    # target = {'interface': "PropertiesInterface",
    #               'method': "getData"}
    # payload = {'ckecksum': checksum,
    #                'client': 1,
    #                'hash': "d751713988987e9331980363e24189ce",
    #                'parameters': []}
    # r = session.post(url,
    #                           params=target,
    #                           data=json.dumps(payload))
    # #print r.content
    # print r.headers
    # cookie = r.headers['set-cookie'].split(';')[0]
    # session.headers.update({"Cookie": cookie})
    #
    # session.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #                         'content-type': 'application/json',
    #                                 "Cookie": "_ym_visorc_22363723=b",
    #                                 "User-Agent": 'Mozilla/5.0 (X11; Ubuntu; \
    #                                 Linux x86_64; rv:26.0) Gecko/20100101 \
    #                                 Firefox/26.0'})

    # c = (url, cookie, checksum)
    # print c
    #
    # game = raillib.Oracle(raillib.Engine(c))

    # tops = [
    #     "2d500ea0-dd75-42ae-48e6-b4e821a2ca81",
    #     "7cac1fdf-e4b7-ad22-0c2b-edddb5854082",
    #     "26b0f71d-c1c1-c70b-e8a8-686733e21ce2",
    #     "b79fa5e0-f5eb-dd2f-595a-91eecb7557d9",
    #     "609bb162-fa49-b9bf-52b6-b2a16ea2e3b5",
    #     "81aa585d-7856-a93f-4ccd-d333221e42d6",
    #     "b199687f-0980-5399-da53-8d22fe2478a4",
    #     "ddd2c2ab-067d-5659-076c-c91343000c4a",
    #     "8e031cfa-726e-0352-acc7-a7eee96df7a4",
    #     "43fcaf03-a9bc-72d5-05b1-a38a408286e2",
    #     "2b3f6aa2-c2a4-5142-95a3-b4bf6bd53282",
    #     "9846e5a0-c87c-cf8d-54c3-b8fb059f4bf9",
    #     "624a760d-efea-63fe-d242-ff9f94e86e26",
    #     "77ca1a37-4c19-0b46-b75b-6c14ce84a197",
    #     "639f1e17-448d-80a4-8708-843b20954740",
    #     "3a458554-4dc6-8b44-6073-b75a456a3d89",
    #     "106e35a2-16a5-5023-20a9-e31a4fdf0ddf",
    #     "377ff58c-2bf9-1bde-28e8-518b85d53f75",
    #     "5a151080-0260-22f9-e90d-c9a7ca401bbb",
    #     "ea7bc805-4f5b-c572-acbd-695ab9391e3f"
    # ]
    # for user in tops:
    #     name = game.get_user(user)['Body']['username'].encode('utf-8')
    #     gold = game.get_resource(user, 2)['Body']['amount']
    #     print name, gold

    # print game.get_resource("2d500ea0-dd75-42ae-48e6-b4e821a2ca81", 2)['Body']['amount']
    # print game.get_user("2d500ea0-dd75-42ae-48e6-b4e821a2ca81")['Body']['username'].encode('utf-8')
    # print game.get_user("2d500ea0-dd75-42ae-48e6-b4e821a2ca81")
    # print game.get_corp("07d2fd4d-dd74-0e12-c648-3e9b299c5c43")

    # corps = {}
    # x = game.get_town_resource("318d7429-1c80-4e10-b93d-abca948def4b", 28)
    # # print x
    # for item in x['Body']:
    #     user = game.get_user(str(item['userId']))['Body']
    #     if 'corporation' in user.keys():
    #         corp = str(user['corporation']['ID'])
    #     else:
    #         corp = "none"
    #
    #     print item['userName'].encode('utf-8'), item['amount']
    #
    #     if corp in corps.keys():
    #         corps[corp] += int(item['amount'])
    #     else:
    #         corps[corp] = int(item['amount'])
    #
    # for corp in corps.keys():
    #     if corp == 'none':
    #         print 'None', corps[corp]
    #         continue
    #     c = game.get_corp(corp)
    #     print c['Body']['name'], corps[corp]


    # a, b = mp.Pipe()
    # x = Monitor('m', a)
    # x()