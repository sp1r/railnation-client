__author__ = 'spir'

import Queue


class Node:
    def __init__(self):
        self.item = None
        self.next_item = None


class Bag:
    def __init__(self):
        self.first = Node()
        self.current = None

    def add(self, new_item):
        old_first = self.first
        self.first = Node()
        self.first.item = new_item
        self.first.next_item = old_first

    def __iter__(self):
        self.current = self.first
        return self

    def next(self):
        tmp = self.current.item
        if tmp is None:
            raise StopIteration
        self.current = self.current.next_item
        return tmp


class Graph:
    def __init__(self, v):
        self.v = v
        self.e = 0
        self.adj_lists = [Bag() for i in range(v)]

    def add_edge(self, v, w):
        self.adj_lists[v].add(w)
        self.adj_lists[w].add(v)
        self.e += 1

    def neighbours(self, v):
        return self.adj_lists[v]


class SymbolGraph(Graph):
    def __init__(self, v):
        Graph.__init__(self, v)
        self.map = {}
        self.keys = {}

    def add_edge(self, v, w):
        if not v in self.map.keys():
            self.keys[len(self.map)] = v
            self.map[v] = len(self.map)
        if not w in self.map.keys():
            self.keys[len(self.map)] = w
            self.map[w] = len(self.map)
        Graph.add_edge(self, self.map[v], self.map[w])

    def neighbours(self, v):
        return Graph.neighbours(self, v)


class BreadthSearch:
    def __init__(self, g, r):
        self.graph = g
        self.root = r
        self.marked = [False for i in range(g.v)]
        self.edge_to = [None for i in range(g.v)]
        self.bfs()

    def bfs(self):
        q = Queue.Queue()
        self.marked[self.root] = True
        q.put(self.root)
        while not q.empty():
            c = q.get()
            for n in self.graph.neighbours(c):
                if not self.marked[n]:
                    self.edge_to[n] = c
                    self.marked[n] = True
                    q.put(n)

    def path_to(self, v):
        path = []
        c = v
        while c != self.root:
            path.append(c)
            c = self.edge_to[c]
        path.append(self.root)
        return path


if __name__ == "__main__":
    x = SymbolGraph(10)
    x.add_edge('asdf', 'fdf')
    x.add_edge('asdf', 'ffff')
    x.add_edge('34353', 'vdvaev')
    x.add_edge('asdf34', 'asdf')
    for i in x.neighbours('asdf'):
        print x.keys[i]