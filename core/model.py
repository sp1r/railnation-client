# -*- coding: utf-8 -*-

__author__ = 'spir'


class Model:
    def __init__(self, kernelgw):
        self.kernel = kernelgw


class Player(Model):
    def __init__(self, kernelgw):
        Model.__init__(self, kernelgw)
        self.name = ""
        self.id = ""
        self.corp_id = ""
        self.prestige = 0
        self.total_trains = 0
        self.profit = 0

    def __repr__(self):
        return "Name: " + self.name + "\nId: " + self.id + \
               "\nPrestige: " + str(self.prestige)

    def corp(self):
        if self.corp_id:
            return self.kernel.get_corp(self.corp_id)
        else:
            return None

    def station(self):
        return self.kernel.get_station(self.id)


class Corporation(Model):
    def __init__(self, kernelgw):
        Model.__init__(self, kernelgw)
        self.name = ""
        self.id = ""
        self.description = ""
        self.prestige = 0
        self.level = 0
        self.home_town_id = ""
        self.member_ids = []

    def __repr__(self):
        return "Name: " + self.name + "\nId: " + self.id + \
               "\nPrestige: " + str(self.prestige) + \
               "\nLevel: " + str(self.level) + \
               "\nMembers: " + str(len(self.member_ids))

    def members(self):
        member_list = []
        for id in self.member_ids:
            member_list.append(self.kernel.get_player(id))
        return member_list


class Building(Model):
    def __init__(self, kernelgw):
        Model.__init__(self, kernelgw)
        self.owner_id = ""
        self.type = 0
        self.name = ""
        self.level = 0
        self.construction_time = 0
        self.money_cost = 0
        self.prestige_gain = 0
        self.max_level = 0
        self.production_time = 0

    def collect(self):
        return self.kernel.collect(self.owner_id, self.type)


class Station(Model):
    def __init__(self, kernelgw):
        Model.__init__(self, kernelgw)
        self.owner_id = ""
        self.buildings = {}

    def __repr__(self):
        line = "Station owner: " + self.owner_id + "\n"
        for btype, building in self.buildings.items():
            line += building.name + ", уровень " + str(building.level) + "\n"
        return line