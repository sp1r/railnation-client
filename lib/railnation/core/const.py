#!/usr/bin/env python
# -*- coding:  utf-8 -*-

building_names = {
    0: 'Engine house',
    1: 'Station concourse',
    2: 'Track production',
    3: 'Construction yard',
    4: 'Bank',
    5: 'License trade',
    6: 'Laboratory',
    7: 'Hotel',
    8: 'Restaurant',
    9: 'Mall',
}

resource_names = {
    0: 'Money',
    1: 'Gold',
    2: 'Prestige',
    3: 'Research points',
    4: '',
    5: '',
    6: '',
    7: '',
    8: '',
    9: 'Free tickets',
    10: '',
    11: '',
    12: '',
    61: '',
    62: '',
    63: '',
    64: '',
    66: '',
    67: '',
    68: '',
    69: '',
    70: '',
    71: '',
    73: '',
    74: ''
}

# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: Trains Depot level=11 build_in_progress=False build_finish_at=2017-01-22 07:44:11.317929 production_at=2017-01-05 14:46:25.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: name level=9 build_in_progress=False build_finish_at=2017-01-23 05:27:59.317929 production_at=2017-01-05 14:46:25.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: name level=8 build_in_progress=False build_finish_at=2017-01-22 14:06:24.317929 production_at=2017-01-05 14:46:25.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: name level=10 build_in_progress=False build_finish_at=2017-01-24 05:25:07.317929 production_at=2017-01-05 14:46:25.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: name level=10 build_in_progress=False build_finish_at=2017-01-21 08:42:22.317929 production_at=2017-01-05 14:46:25.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: name level=2 build_in_progress=False build_finish_at=2017-01-17 09:07:41.317929 production_at=2017-01-05 14:46:25.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager:  level=11 build_in_progress=False build_finish_at=2017-01-23 21:35:33.317929 production_at=2017-01-24 07:58:53.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: Hotel level=10 build_in_progress=True build_finish_at=2017-01-24 10:31:12.317929 production_at=2017-01-24 09:34:47.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: Restaurant level=17 build_in_progress=False build_finish_at=2017-01-23 11:35:30.317929 production_at=2017-01-24 08:04:47.317929 video_watched=False
# 2017-24-01 07:37:58:    DEBUG: RailNation.StationManager: Mall level=13 build_in_progress=True build_finish_at=2017-01-24 11:50:57.317929 production_at=2017-01-24 09:30:25.317929 video_watched=False
