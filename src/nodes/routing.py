from nodes import basic

class IpNode(basic.BroadcastNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routes = dict(zip(*[['A','B','C']]*2))

    def recv(self, msg, link):
        self.debug('received:%s' % msg)

    def init_cli(self):
        super().init_cli()
        self.cli.add_func(self.send_to, 'send', ('host', {'help': 'host to send to'}),
                                  ('protocol', {'help': 'protocol number of message', 'type': int}),
                                  ('msg', {'help': 'body of message'}))
        self.cli.add_func(self.disp_routes, 'routes')

    def disp_routes(self):
        self.debug(self.routes)

    def send_to(self, host, protocol, msg):
        self.debug('sending message %s to %s on proto %s' % (msg, host, protocol))
        if host in self.routes:
            next_hop = self.routes[host]
            if next_hop in self.links:
                self.links[next_hop].send(self.pack_msg(host, protocol, msg))
            else:
                self.debug("WTF bad entry in route table: %s next hop for %s" % (host, next_hop))
        else:
            self.debug('dropping packet for %s' % host)

    def send_routes(self, host):
        pass

    def pack_msg(self, host, proto, msg):
        return "%s:%s" % (proto, msg)

