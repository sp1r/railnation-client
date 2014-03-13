# -*- coding: utf-8 -*-

__author__ = 'spir'

import model
import raillib


def parse_player(payload, gw):
    player = model.Player(gw)
    data = payload['Body']

    player.id = str(data['user_id'])
    player.name = data['username'].encode("utf-8")
    if "corporation" in data.keys():
        player.corp_id = str(data['corporation']['ID'])
    else:
        player.corp_id = None
    player.prestige = int(data['prestige'])
    player.total_trains = int(data['amountOfTrains'])
    player.profit = int(data['salesToday'])
    return player


def parse_corp(payload, gw):
    corp = model.Corporation(gw)
    data = payload['Body']

    corp.id = str(data['ID'])
    corp.name = data['name'].encode("utf-8")
    corp.description = data['description'].encode("utf-8")
    corp.prestige = float(data['prestige'])
    corp.level = int(data['level'])
    corp.home_town_id = str(data['homeTown'])
    for item in data['members']:
        if item['title'] == '3':
            continue
        corp.member_ids.append(str(item['user_id']))
    return corp


def parse_station(payload, gw, owner_id):
    station = model.Station(gw)
    station.owner_id = owner_id

    for btype in payload['Body'].keys():
        station.buildings[int(btype)] = \
            parse_building(payload['Body'][btype], gw, owner_id)

    return station


def parse_building(data, gw, owner_id):
    building = model.Building(gw)
    building.owner_id = owner_id
    building.type = int(data['type'])
    building.name = raillib.buildings[building.type]
    building.level = int(data['level'])
    building.construction_time = int(data['constructionTime'])
    building.money_cost = -int(data['resourcesNext']['1'])
    building.prestige_gain = int(data['resourcesNext']['3'])
    building.max_level = int(data['maxLevel'])
    building.production_time = int(data['productionTime'])
    return building


def parse_collecting_result(payload):
    if payload["Errorcode"] == 10054:
        return 'overflow'
    elif not payload["Body"]:
        return 'failure'
    else:
        return 'success'


def parse_lottery(payload):
    if payload['Body']['freeSlot']:
        return True
    return False


def parse_reward(payload):
    return payload