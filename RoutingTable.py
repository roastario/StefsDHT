# bep_0005 specifies to use the XOR Metric (ie, the distance between two nodes is the XOR value of their ids)

def _strxor(a, b):
    """ xor two strings of different lengths """
    if len(a) > len(b):
        return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a[:len(b)], b)])
    else:
        return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b[:len(a)])])


class Bucket(object):
    CAPACITY = 8

    def __init__(self, min_id, max_id):
        self.nodes = []
        self.min_id = min_id
        self.max_id = max_id

    def has_capacity(self):
        return len(self.nodes) >= Bucket.CAPACITY


class RoutingTable(object):
    def __init__(self):
        self.buckets = []
