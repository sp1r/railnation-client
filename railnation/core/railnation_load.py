# -*- coding:utf-8 -*-
"""docstring"""

import railnation.core.railnation_globals as global_vars


def load_game(client):
    client.session.headers.update({'content-type': 'application/json'})

    client.player_id = client.produce('AccountInterface',
                                      'is_logged_in',
                                      [client.webkey])['Body']
    if not client.player_id:
        print('Cannot load game. Not authorised')
        exit(1)

    props = client.produce('PropertiesInterface',
                           'getData',
                           [])['Body']

    global_vars.properties = props['properties']
    global_vars.properties['client'] = props['client']

    global_vars.client = client