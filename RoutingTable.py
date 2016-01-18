import math

from Swarm import Node


# bep_0005 specifies to use the XOR Metric (ie, the distance between two nodes is the XOR value of their ids)
def _strxor(a, b):
    """ xor two strings of different lengths """
    if len(a) > len(b):
        return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a[:len(b)], b)])
    else:
        return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b[:len(a)])])


# CONTRACT IS, IF COMPARATOR EVALUATES TO > 1, THE ITEM WE JUST ASKED ABOUT IS LARGER THAN THE ONE WE CURRIED IN
def search_sorted_list(items, comparator, startIdx, endIdx):
    if startIdx == endIdx:
        return None

    idx = startIdx + int(math.ceil((endIdx - startIdx) / 2))

    while True:
        # the comparator has a curried item in it (ie, the item we are looking for)
        comparison_result = comparator(items[idx])

        if comparison_result == 0:
            # SUCCESS, we have found the thing
            return items[idx]
        elif comparison_result > 0:
            new_start_idx = idx + 1
            new_end_idx = endIdx
            return search_sorted_list(items, comparator,
                                      new_start_idx, new_end_idx)
        elif comparison_result < 0:
            new_start_idx = startIdx
            new_end_idx = idx - 1

            return search_sorted_list(items, comparator,
                                      new_start_idx, new_end_idx)


class Bucket(object):
    CAPACITY = 8

    def __init__(self, min_id, max_id):
        self.nodes = []
        self.min_id = min_id
        self.max_id = max_id

    def has_capacity(self):
        return len(self.nodes) >= Bucket.CAPACITY

    def add_node(self, node_to_add):
        self.nodes.append(node_to_add)

    @staticmethod
    def build_comparator_for_node(id_to_fit_into_bucket):
        def id_based_bucket_comparator(bucket_to_check):
            if bucket_to_check.min_id <= id_to_fit_into_bucket < bucket_to_check.max_id:
                # the id is within the range of this bucket
                return 0
            else:
                return id_to_fit_into_bucket - bucket_to_check.min_id

        return id_based_bucket_comparator


class RoutingTable(object):
    MAX_NUMBER_OF_BUCKETS = int(pow(2, 16))
    MAX_ID = 32
    MIN_ID = 0

    def __init__(self):
        self.buckets = [Bucket(RoutingTable.MIN_ID, RoutingTable.MAX_ID / 2),
                        Bucket(RoutingTable.MAX_ID / 2 + 1, RoutingTable.MAX_ID)]

    def add_node(self, node):
        bucket = self.find_node_bucket(node)
        bucket.add_node(node)

    def find_node_bucket(self, node):
        return search_sorted_list(self.buckets, Bucket.build_comparator_for_node(node.long_id), 0, len(self.buckets))

    def __repr__(self):
        pass


table = RoutingTable()

for i in range(1, 32):
    node = Node(("123.1.2.3", 456), str(i))
    print "adding + " + str(node)
    table.add_node(node)

print table
