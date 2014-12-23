import multiprocessing
import selectors

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
                    print("Bad line '%s' in Topology File. Exiting." % line)
                    sys.exit(1)
    
    def _parse_node(self, line):
        import nodes
        _, name, cls, *rest = line.split()
        self.nodes[name] = eval(cls)(name, *rest)

    def _parse_link(self, line):
        h1, h2 = line.split(' <-> ')
        h1_con, h2_con = NetLink.link_pair(h1, h2) 
        self.nodes[h1].add_link(h1_con, self.nodes[h2])
        self.nodes[h2].add_link(h2_con, self.nodes[h1])

    def get_nodes(self):
        return self.nodes.values()

class NetNode(object):

    def __init__(self, name):
        self.name  = name
        self.links = {}
        self.cli   = cli.CLI()
        self.cli.add_func(lambda: print(self.links), 'links')
        self.running = True
        self.init_cli()

        self.selector = selectors.DefaultSelector()

    def die(self):
        self.running = False

    def get_name(self):
        return self.name

    def add_link(self, link, host):
        self.links[host.get_name()] = link 
        self.selector.register(link.get_conn(), selectors.EVENT_READ, self.handle_incoming)

    def handle_incoming(self, link):
        raise NotImplementedError

    # kill by sending control frame?
    def run(self):
        while self.running:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def get_cli(self):
        return self.cli

    def debug(self, s):
        print("%s:%s" % (self.get_name(), s))


class NetLink(object):

    def __init__(self, connection, **kwargs):
        self.cnx = connection

    @classmethod
    def link_pair(cls, host1, host2, **kwargs):
        h1conn, h2conn = multiprocessing.Pipe()
        h1toh2 = cls(h1conn, **kwargs)
        h2toh1 = cls(h2conn, **kwargs)
        return h1toh2, h2toh1

    def get_conn(self):
        return self.cnx

    def send(self, msg):
        self.cnx.send(msg)

    def recv(self):
        return self.cnx.recv()
