# -*- coding:utf-8 -*-
"""docstring"""

try:
    import queue
except ImportError:
    import Queue as queue


class WeightedEdge:
    def __init__(self, to, dist):
        self.to = to
        self.dist = dist

    def __str__(self):
        return "to: " + self.to + " dist: " + str(self.dist)


class WeightedGraph:
    def __init__(self):
        self.v = 0
        self.e = 0
        self.adj = {}

    def add_vertex(self, v):
        self.adj[v] = []
        self.v += 1

    def add_edge(self, v1, v2, dist):
        self.adj[v1].append(WeightedEdge(v2, dist))
        self.adj[v2].append(WeightedEdge(v1, dist))
        self.e += 1

    def read_vertexes_from_file(self, input_file):
        for line in input_file:
            self.add_vertex(line.strip())

    def read_edges_from_file(self, input_file):
        for line in input_file:
            v1, v2, d = line.strip().split()
            self.add_edge(v1, v2, int(d))


class BellmanFordSP:
    def __init__(self, graph, root):
        self.graph = graph
        self.is_in_queue = {}
        self.edge_to = {}
        self.dist_to = {}

        for vertex in graph.adj.keys():
            self.is_in_queue[vertex] = False
            self.edge_to[vertex] = 0
            self.dist_to[vertex] = float("inf")

        self.root = root
        self.dist_to[self.root] = 0

        self.search_queue = queue.Queue()
        self.search_queue.put(self.root)
        self.is_in_queue[self.root] = True
        while not self.search_queue.empty():
            self.relax(self.search_queue.get())

    def relax(self, vertex):
        for w in self.graph.adj[vertex]:
            if self.dist_to[w.to] > self.dist_to[vertex] + w.dist:
                self.dist_to[w.to] = self.dist_to[vertex] + w.dist
                self.edge_to[w.to] = vertex
                if not self.is_in_queue[w.to]:
                    self.search_queue.put(w.to)
                    self.is_in_queue[w.to] = True

    def get_dist_to(self, v):
        return self.dist_to[v]

    def has_path_to(self, v):
        return self.dist_to[v] < float("inf")

    def path_to(self, v):
        if not self.has_path_to(v):
            return None
        path = queue.LifoQueue()
        current = v
        while current != self.root:
            path.put(current)
            current = self.edge_to[current]
        path.put(self.root)
        return path