import binascii


class Node(object):
    def __init__(self, address, node_id=None):
        self.address = address
        if node_id:
            self.id = node_id

            hex_id = binascii.b2a_hex(node_id)
            self.long_id = long(hex_id, base=16)

    def __repr__(self):
        return "Node " + str(self.id) + " @ " + str(self.address)
