#!/usr/bin/python
# -*- coding: utf-8 -*-

author__ = 'spir'

import botlib

################################################################################
# Connection parameters

webkey = "42cbf556576ddc85a560ff2d7909c020"

url = "http://s6.railnation.ru/web/rpc/flash.php"
cookie = "PHPSESSID=oga2i95f5qpn2mvmsof5t675e3"
checksum = "3caf8214532b258daf0118304972727e"

conn = (url, cookie, checksum)

################################################################################
# Options

bots = {
    'main'      : None,
    'switch'    : botlib.Switch,
    'log'       : botlib.Chronicler,
    'game'      : botlib.Messenger,
    'collect'   : botlib.Stranger,
    'judge'     : botlib.Judge,
    'repair'    : botlib.Mechanic,
    'test'      : botlib.Test,
    'research'  : botlib.Scientist,
}