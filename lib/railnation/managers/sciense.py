#!/usr/bin/env python
# -*- coding:  utf-8 -*-

import pprint
import heapq
try:
    import queue
except ImportError:
    import Queue as queue

from threading import Lock

import cherrypy
from cherrypy.process.plugins import Monitor

from railnation.core.common import log
from railnation.core.server import server
from railnation.managers.properties import PropertiesManager
from railnation.managers.avatar import AvatarManager
from railnation.managers.properties import PropertiesManager
from railnation.managers.resources import ResourcesManager
from railnation.core.errors import RailNationClientError


class TechGraph:
    """
    Graph of technologies.
    """
    def __init__(self):
        self.provide = {}  # Providing matrix
        self.req = {}  # Requirements matrix
        self.cost = {}  # Requirements cost

    def set_cost(self, tech_id, research_cost):
        self.cost[tech_id] = research_cost

    def set_req(self, tech_id, satisfy_list):
        try:
            self.req[tech_id].append(satisfy_list)
        except KeyError:
            self.req[tech_id] = [satisfy_list]

        for item in satisfy_list:
            try:
                self.provide[item].append(tech_id)
            except KeyError:
                self.provide[item] = [tech_id]

    def get_req(self, tech_id):
        try:
            return self.req[tech_id]
        except KeyError:
            return []

    def get_provide(self, tech_id):
        try:
            return self.provide[tech_id]
        except KeyError:
            return []

    def get_pathfinder(self):
        return RLF(self, '000000')


class SimplePQ:
    def __init__(self):
        self.queue = []

    def push(self, item, weight):
        heapq.heappush(self.queue, (weight, item))

    def pop(self):
        return heapq.heappop(self.queue)[1]

    def contains(self, item):
        return item in [i[1] for i in self.queue]

    def empty(self):
        return len(self.queue) == 0


class RLF:
    """
    Requirements List Finder.
    """
    def __init__(self, graph, root):
        self.graph = graph
        self.root = root
        self.cost_to = {}
        self.edges_to = {}
        for i in graph.cost.keys():
            self.cost_to[i] = float("inf")
            self.edges_to[i] = []
        self.cost_to[root] = 0

        self.pq = SimplePQ()
        self.pq.push(root, 0)
        while not self.pq.empty():
            self._relax_vertex(self.pq.pop())

    def _relax_vertex(self, v):
        for w in self.graph.get_provide(v):
            all_reqs = self.graph.get_req(w)
            for path in all_reqs:
                path_cost = self.graph.cost[w]
                for r in path:
                    path_cost += self.cost_to[r]
                if path_cost < self.cost_to[w]:
                    self.cost_to[w] = path_cost
                    self.edges_to[w] = path
            if not self.pq.contains(w):
                self.pq.push(w, self.cost_to[w])

    def cost_to(self, v):
        return self.cost_to[v]

    def has_path_to(self, v):
        return self.cost_to[v] < float('inf')

    def path_to(self, v):
        if not self.has_path_to(v):
            return []

        path = []
        q = queue.Queue()
        q.put(v)
        while not q.empty():
            n = q.get()
            if n in path:
                path.remove(n)
            path.append(n)
            for i in self.edges_to[n]:
                q.put(i)

        return path[::-1]


class ScienceManager:
    """
    Manager of Research tree.
    """

    instance = None

    @staticmethod
    def get_instance():
        """
        :rtype: ScienceManager
        """
        if ScienceManager.instance is None:
            ScienceManager.instance = ScienceManager()
        return ScienceManager.instance

    def __init__(self):
        self.log = log.getChild('ScienceManager')
        self.log.debug('Initializing...')
        self.tech = {}
        self.tech_graph = TechGraph()
        self.tech_path_finder = None

        self.research_lock = Lock()
        self.research_path = []

    def load_tech_tree(self):
        self.log.debug('Loading technologies...')
        # Root object to prepare graph
        self.tech['000000'] = {
            'name': 'Root',
            'type': '',
            'era': 0,
            'cost': 0,
            'spent': 0,
            'require_one_of_this_combinations': [[]],
        }
        self.tech_graph.set_cost('000000', 0)
        # First train is missing from server info (always available)
        self.tech['110100'] = {
            'name': 'Loc 1',
            'type': 'train',
            'parent': '110100',
            'era': 1,
            'cost': 0,
            'spent': 0,
            'require_one_of_this_combinations': [[]],
        }
        self.tech_graph.set_cost('110100', 0)
        self.tech_graph.set_req('110100', ['000000'])

        raw_tech_tree = PropertiesManager.get_instance().get_tech_tree()
        self.log.debug('Loaded %s raw tech descriptions' % len(raw_tech_tree))

        # load tech static data
        for tech_id, tech_data in raw_tech_tree.items():
            tech_id = str(tech_id)
            tech = {
                'name': tech_data['name'],
                'parent': tech_id,
                'type': '',
                'era': 1,
                'cost': 0,
                'spent': 0,
                'require_one_of_this_combinations': [[]],
            }

            if tech_id[0] == '1':
                tech['type'] = 'train'
            elif tech_id[3] == '0':
                tech['type'] = 'coupling'
            else:
                tech['type'] = 'upgrade'
                tech['parent'] = '1%s00' % tech_id[1:4]

            for item in tech_data['check']:
                if item['func'] == 'getResearchPointsForTech':
                    tech['cost'] = int(item['return']['>='])

                elif item['func'] == 'getCurrentEra':
                    tech['era'] = int(item['return']['>=']) + 1

                elif item['func'] == 'hasTech':
                    tech['require_one_of_this_combinations'][0].append(str(item['param'][0]))

                elif item['func'] == 'hasOneOfTheseTechCombinations':
                    tech['require_one_of_this_combinations'] = [[str(k) for k in i] for i in item['param']]

            self.log.debug('Technology %s: %s' % (tech_id, pprint.pformat(tech)))
            self.tech[tech_id] = tech

        self.log.debug('%s technologies loaded' % len(self.tech))

        self.log.debug('Loading spent points')
        r = server.call('ResearchInterface', 'get', [AvatarManager.get_instance().id])
        for tech in r:
            if tech['isResearched'] == '1':
                self.tech[str(tech['techID'])]['spent'] = self.tech[str(tech['techID'])]['cost']
            else:
                self.tech[str(tech['techID'])]['spent'] = int(tech['amount'])
            self.log.debug('%s/%s spent on %s (%s)' % (
                tech['amount'],
                self.tech[str(tech['techID'])]['cost'],
                str(tech['techID']),
                'Reached' if self.tech[str(tech['techID'])]['spent'] == self.tech[str(tech['techID'])]['cost'] else 'Not reached'
            ))

        self.log.debug('Constructing tech graph')
        for tech_id, tech_data in self.tech.items():
            if tech_id in ['000000', '110100']:
                continue

            self.tech_graph.set_cost(tech_id, tech_data['cost'] - tech_data['spent'])

            if not tech_data['require_one_of_this_combinations'][0]:
                if tech_data['parent'] == '110100':
                    # first era misses its firs train from config
                    self.tech_graph.set_req(tech_id, ['110100'])
                else:
                    # first tech of era
                    self.tech_graph.set_req(tech_id, ['000000'])
            else:
                for group in tech_data['require_one_of_this_combinations']:
                    self.tech_graph.set_req(tech_id, group)

    def research(self, tech_id, amount=None):
        self.log.debug('Waiting for research lock...')
        with self.research_lock:
            self.log.debug('Research lock aquired')
            return self._research(tech_id, amount)

    def _research(self, tech_id, amount):
        if amount is None:
            amount = ResourcesManager.get_instance().science_points
        else:
            amount = int(amount)
        tech_id = str(tech_id)

        if self.tech[tech_id]['era'] > AvatarManager.get_instance().era:
            self.log.error('Cannot research technologies or next era (current: %s, tech: %s)' %
                           (AvatarManager.get_instance().era, self.tech[tech_id]['era']))
            return False

        points_available = ResourcesManager.get_instance().science_points
        if points_available < amount:
            self.log.error('Cannot spend %s points, got only %s' % (amount, points_available))
            return False

        if self.tech_path_finder is None:
            self.tech_path_finder = self.tech_graph.get_pathfinder()

        if self.tech_path_finder.cost_to[tech_id] != self.tech_graph.cost[tech_id]:
            self.log.error('Tech %s is locked. Cannot research' % tech_id)
            return False

        points_needed = self.tech_graph.cost[tech_id]
        self.log.debug('Technology requires %s points' % points_needed)

        if points_needed <= 0:
            self.log.warning('Technology %s already researched' % tech_id)
            return True

        elif points_needed < amount:
            amount = points_needed

        self.log.debug('Researching %s for %s points' % (tech_id, amount))

        r = server.call('ResearchInterface', 'research', [int(tech_id), amount])
        self.tech[tech_id]['spent'] += amount
        self.tech_graph.cost[tech_id] -= amount
        self.tech_path_finder = None
        if r:
            if self.tech[tech_id]['spent'] == self.tech[tech_id]['cost']:
                self.log.info('Technology researched: %s' % self.tech[tech_id]['name'])

            else:
                error_msg = 'Calculation mismatch! Possible research points corruption!'
                self.log.critical(error_msg)
                raise RailNationClientError(error_msg)

        return True

    def path_to(self, tech_id):
        tech_id = str(tech_id)
        if tech_id not in self.tech:
            self.log.warning('Unknown tech: %s' % tech_id)
            return []

        self.log.debug('Constructing path to: %s' % tech_id)

        if self.tech_path_finder is None:
            self.tech_path_finder = self.tech_graph.get_pathfinder()

        result = []
        for step in self.tech_path_finder.path_to(tech_id):
            self.log.debug('Step: %s %s %s' % (step, self.tech[step]['name'], self.tech_graph.cost[step]))
            if self.tech_graph.cost[step] != 0:
                result.append(step)
            else:
                self.log.debug('Skipping researched tech: %s' % step)
        self.log.debug('Returning path of %s steps' % len(result))
        return result

    def schedule_researching(self, tech_id):
        tech_id = str(tech_id)
        self.log.debug('Add tech %s to schedule' % tech_id)

        if tech_id not in self.tech.keys():
            self.log.error('Unknown technology ID: %s' % tech_id)
            return False

        extra_path = [i for i in self.path_to(tech_id) if i not in self.research_path]
        self.log.debug('Appending to research path: %s' % extra_path)
        self.research_path.extend(extra_path)
        self.check()
        return self.research_path

    def cancel_researching(self):
        self.log.debug('Clearing research schedule')
        with self.research_lock:
            self.research_path = []
        return self.research_path

    def check(self):
        if not self.research_path:
            return

        if ResourcesManager.get_instance().science_points == 0:
            return

        target = self.research_path[0]

        self.log.debug('Researching: %s' % target)

        r = self.research(target)

        if r:
            self.log.debug('Research successful')
            if self.tech[target]['spent'] >= self.tech[target]['cost']:
                self.log.debug('Completed %s' % target)
                self.research_path = self.research_path[1:]
                self.log.debug('Check next research in path')
                self.check()


Monitor(cherrypy.engine, ScienceManager.get_instance().check, frequency=900, name='Researcher').subscribe()

