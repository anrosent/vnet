#!/usr/bin/env python3
import sys
import argparse
import multiprocessing
import selectors

from threading import Thread
import cli


class NetTopology(object):

    def __init__(self, topo_fn):
        self.nodes = {}
        self.parse_file(topo_fn)

    def parse_file(self, topo_fn):
        with open(topo_fn, 'r') as f:
            for line in filter(lambda line: line, f):
                line = line.strip()
                try:
                    if line.startswith('node'):
                        self._parse_node(line)
                    else:
                        self._parse_link(line)
                except ValueError as e:
                    print(e)
                    print("Bad line '%s' in Topology File. Exiting." % line)
                    sys.exit(1)
    
    def _parse_node(self, line):
        _, name, cls, *rest = line.split()
        self.nodes[name] = eval(cls)(name, *rest)

    def _parse_link(self, line):
        h1, h2 = line.split(' <-> ')
        h1_con, h2_con = multiprocessing.Pipe()
        self.nodes[h1].add_link(h1_con, self.nodes[h2])
        self.nodes[h2].add_link(h2_con, self.nodes[h1])

    def get_nodes(self):
        return self.nodes.values()

class NetNode(object):

    def __init__(self, name):
        self.name  = name
        self.links = {}
        self.cli   = cli.CLI()
        self.selector = selectors.DefaultSelector()
        self.init_cli()

    def get_name(self):
        return self.name

    def add_link(self, link, host):
        self.links[host.get_name()] = link 
        self.selector.register(link, selectors.EVENT_READ, self.handle_incoming)

    def handle_incoming(self, link):
        raise NotImplementedError

    #TODO: select loop, calling overridden handleMsg function
    def run(self):
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def get_cli(self):
        return self.cli

    def print(self, s):
        print("%s:%s" % (self.get_name(), s))

class DebugNode(NetNode):

    def __init__(self, name):
        super().__init__(name)

    def init_cli(self):
        self.cli.add_func(lambda: print(self.links), 'links')


class HiNode(NetNode):

    def init_cli(self):
        self.cli.add_func(self.broadcast_hi, 'hiall')
        self.cli.add_func(lambda: print(self.links), 'links')

    def broadcast_hi(self):
        for name, link in self.links.items():
            link.send('hi')
    
    def handle_incoming(self, link, mask):
        msg = link.recv()
        self.print("Got msg %s"%msg)

class BroadcastNode(NetNode):
    def init_cli(self):
        self.cli.add_func(self.broadcast, 'msgcast', ('msg', {'help': 'message to send'}))
        self.cli.add_func(lambda: print(self.links), 'links')

    def broadcast(self, msg="hi"):
        for name, link in self.links.items():
            link.send(msg)
    
    def handle_incoming(self, link, mask):
        msg = link.recv()
        self.print("Got msg %s"%msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topology_file', help='file containing the virtual network topology specification')
    args = parser.parse_args()

    # Parse topology spec
    topology = NetTopology(args.topology_file) 

    # Build driver
    driver = cli.CLI()
    for node in topology.get_nodes():
        driver.add_cli(node.get_name(), node.get_cli())

    # Activate virtual network
    node_threads = [Thread(target=node.run) for node in topology.get_nodes()]
    for t in node_threads:
        t.start()

    # Run driver
    driver.run()

    # Driver is done, wait for threads
    for t in node_threads:
        t.join()

    print("Virtual network successfully brought down.")
