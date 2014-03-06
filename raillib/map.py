__author__ = 'spir'

import maputils

global_map = maputils.WeightedGraph()
with open('raillib/vertex', 'r') as v:
    global_map.read_vertexes_from_file(v)
with open('raillib/edges', 'r') as e:
    global_map.read_edges_from_file(e)

