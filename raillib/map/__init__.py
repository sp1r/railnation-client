# -*- coding:utf-8 -*-
"""docstring"""

from raillib.map.maputils import WeightedGraph

global_map = WeightedGraph()

with open('raillib/map/vertex', 'r') as v:
    global_map.read_vertexes_from_file(v)

with open('raillib/map/edges', 'r') as e:
    global_map.read_edges_from_file(e)