from core import NetNode

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
        self.debug("Got msg %s"%msg)

class BroadcastNode(NetNode):
    def init_cli(self):
        self.cli.add_func(self.broadcast, 'msgcast', ('msg', {'help': 'message to send', 'nargs':'?'}))

    def broadcast(self, msg="hi"):
        for name, link in self.links.items():
            link.send(msg)
    
    def handle_incoming(self, link, mask):
        msg = link.recv()
        self.debug("Got msg %s"%msg)

class EchoNode(NetNode):
    def handle_incoming(self, link, mask):
        msg = link.recv()
        link.send(msg)
        self.debug("Echoing %s" % msg)

    def init_cli(self):
        pass
