#!/usr/bin/python
# -*- coding: utf-8 -*-

#import core.client
import time
import utils
import shelve
import json
import multiprocessing as mp
import base64

__author__ = 'spir'


# s6 old
URL = "http://s6.railnation.ru/web/rpc/flash.php"
COOKIE = "PHPSESSID=a5hbtpnefl2kgb9e5vvkvmlsu0"  # s6
CHECKSUM = "3caf8214532b258daf0118304972727e"  # s6

CONN = (URL, COOKIE, CHECKSUM)

#game = core.client.Oracle(core.client.Engine(CONN))

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

# def get_town_num(dict, num):
#     for town in dict['Body']:
#             if town['name'] == num:
#                 return town
#     return None

if __name__ == '__main__':
    # js = '{"data":2,"name":"hello"}'
    # d = json.loads(js)
    # print d
    # class Test:
    #     def __init__(self, some=None, id=None):
    #         if some is not None:
    #         #print "inside class", some
    #             self.data = some['data']
    #             self.name = some['name']
    #         else:
    #             self.data = id
    #             self.name = 'empty'
    #
    # c = json.loads(js, object_hook=Test)
    # print c.data, c.name
    # b = Test(id=3)
    # print b.data, b.name

    with open('docs/b64.t', 'rb') as b:
        x = b.read()
    x = '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'
    with open('docs/b64.img', 'wb') as i:
        i.write(base64.b64decode(x))

    # name = 33
    # tpl_cons = "{:08.6f}"
    # tpl_fac = "{0:d}/{1:d}"
    # last_cons = 0
    # while True:
    #     t = game.get_town_brief("318d7429-1c80-4e10-b93d-abca948def4b") # нью
    #     #t = game.get_town_brief("ef07f109-81bc-4f04-a185-7048a64fa984") # рокс
    #     p = game.get_statistics_towns()
    #     new_vasuki = get_town_num(p, '33')
    #     #print time.strftime('%H:%M:%S'),
    #     print t['Body']['town']['level'],
    #     print new_vasuki['depots'],
    #     # f = game.get_all_locations()
    #     # state0_num = 0
    #     # state0_lvl = 0
    #     # state1_num = 0
    #     # state1_lvl = 0
    #     # state2_num = 0
    #     # state2_lvl = 0
    #     # for factory in f['Body']:
    #     #     if factory['city_location_id'] == "318d7429-1c80-4e10-b93d-abca948def4b":
    #     #         if factory['factoryState'] == 0:
    #     #             state0_num += 1
    #     #             state0_lvl += factory['level']
    #     #         elif factory['factoryState'] == 1:
    #     #             state1_num += 1
    #     #             state1_lvl += factory['level']
    #     #         elif factory['factoryState'] == 2:
    #     #             state2_num += 1
    #     #             state2_lvl += factory['level']
    #     # print tpl_fac.format(state0_lvl, state0_num),
    #     # print tpl_fac.format(state1_lvl, state1_num),
    #     # print tpl_fac.format(state2_lvl, state2_num),
    #     # print tpl_fac.format(state0_lvl+state1_lvl+state2_lvl, state0_num+state1_num+state2_num),
    #     for x in t['Body']['resources']:
    #         if x['priority'] == 1:
    #             print x['consume_amount'],
    #             print x['amount'],
    #             try:
    #                 print tpl_cons.format(x['consume_amount']*1.0/x['amount']),
    #             except ZeroDivisionError:
    #                 print '-',
    #     print
    #     time.sleep(60)
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