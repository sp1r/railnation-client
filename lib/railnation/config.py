#!/usr/bin/env python
# -*- coding:  utf-8 -*-

# Connection parameters
MAX_RECONNECT = 5
CONNECTION_TIMEOUT = 3


# Game parameters:
BASE_URL = 'http://www.rail-nation.com'
LOBBY_URL = 'http://lobby.rail-nation.com'

# CLIENT_CHECKSUM = 'ea24d4af2c566004782f750f940615e5'  # Where to get this value from?
CLIENT_CHECKSUM = -1  # and why not?

# Mellon config 
# TODO: acquire it dynamically
MELLON_CONFIG = {
    'domain': 'www.rail-nation.com',
    'path': '/home/',
    'inGame': '0',
    'id': 'railnation',
    'countryId': 'ii',
    'instanceId': 'portal-ii',
    'languageId': 'en_GB',
    'cookieEnabled': '1',
}
XDM_CONFIG = {
    'msname': 'msid',
    'xdm_e': 'http://www.rail-nation.com',
    'xdm_c': 'default1158',
    'xdm_p': 1
}