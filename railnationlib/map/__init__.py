# -*- coding:utf-8 -*-
"""docstring"""

from railnationlib.map.maputils import (
    WeightedGraph,
    BellmanFordSP
)


class Map(object):
    def __init__(self):
        self.graph = WeightedGraph()
        with open('railnationlib/map/vertex', 'r') as v:
            for line in v:
                self.graph.add_vertex(line.strip())

        self.distances = {}
        with open('railnationlib/map/edges', 'r') as e:
            for line in e:
                v1, v2, dist = line.strip().split()
                d = int(dist)

                try:
                    self.distances[v1][v2] = d
                except KeyError:
                    self.distances[v1] = {v2: d}

                try:
                    self.distances[v2][v1] = d
                except KeyError:
                    self.distances[v2] = {v1: d}

    def add_edge(self, v1, v2):
        self.graph.add_edge(v1, v2, self.distances[v1][v2])

    def get_route(self, v1, v2):
        alg = BellmanFordSP(self.graph, v1)

        if alg.has_path_to(v2):
            return alg.path_to(v2)

        else:
            return None