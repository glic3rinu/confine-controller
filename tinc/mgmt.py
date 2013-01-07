class TincBackend(object):
    def address(self, node):
        return node.tinc.address


backend = TincBackend()
