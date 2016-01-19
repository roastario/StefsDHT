import math
import os

from Swarm import Node


# bep_0005 specifies to use the XOR Metric (ie, the distance between two nodes is the XOR value of their ids)
def _strxor(a, b):
    """ xor two strings of different lengths """
    if len(a) > len(b):
        return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a[:len(b)], b)])
    else:
        return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b[:len(a)])])


# CONTRACT IS, IF COMPARATOR EVALUATES TO > 1, THE ITEM WE JUST ASKED ABOUT IS LARGER THAN THE ONE WE CURRIED IN
def fucksake_why_isnt_this_std_lib_search_sorted_list(items, comparator, startIdx, endIdx):
    if startIdx == endIdx:
        return items[startIdx] if comparator(items[startIdx]) == 0 else None, startIdx
    else:
        idx = startIdx + int(math.ceil((endIdx - startIdx) / 2))

    while True:
        # the comparator has a curried item in it (ie, the item we are looking for)
        comparison_result = comparator(items[idx])

        if comparison_result == 0:
            # SUCCESS, we have found the thing
            # lets use the ONE return point defined above - inefficient I know.
            return fucksake_why_isnt_this_std_lib_search_sorted_list(items, comparator, idx, idx)
        elif comparison_result > 0:
            new_start_idx = idx + 1
            new_end_idx = endIdx
            return fucksake_why_isnt_this_std_lib_search_sorted_list(items, comparator,
                                                                     new_start_idx, new_end_idx)
        elif comparison_result < 0:
            new_start_idx = startIdx
            new_end_idx = idx - 1

            return fucksake_why_isnt_this_std_lib_search_sorted_list(items, comparator,
                                                                     new_start_idx, new_end_idx)


class Bucket(object):
    CAPACITY = 8

    def __init__(self, min_id, max_id):
        self.nodes = []
        self.min_id = min_id
        self.max_id = max_id

    def has_capacity(self):
        return not len(self.nodes) >= Bucket.CAPACITY

    def add_node(self, node_to_add):
        self.nodes.append(node_to_add)

    @staticmethod
    def build_comparator_for_node(id_to_fit_into_bucket):
        def id_based_bucket_comparator(bucket_to_check):
            if bucket_to_check.min_id <= id_to_fit_into_bucket <= bucket_to_check.max_id:
                # the id is within the range of this bucket
                return 0
            else:
                return id_to_fit_into_bucket - bucket_to_check.min_id

        return id_based_bucket_comparator


class RoutingTable(object):
    MAX_NUMBER_OF_BUCKETS = int(pow(2, 16))
    MAX_ID = long(pow(2, 160)) - 1
    MIN_ID = 0

    def __init__(self):
        self.buckets = [Bucket(RoutingTable.MIN_ID, RoutingTable.MAX_ID / 2),
                        Bucket(RoutingTable.MAX_ID / 2, RoutingTable.MAX_ID)]

    def add_node(self, node):
        bucket = self.find_node_bucket(node)
        bucket.add_node(node)

    def find_node_bucket(self, node):
        search_result = fucksake_why_isnt_this_std_lib_search_sorted_list(self.buckets,
                                                                          Bucket.build_comparator_for_node(
                                                                              node.long_id),
                                                                          0, len(self.buckets) - 1)
        found_bucket = search_result[0]
        if not found_bucket:
            # we did not find a bucket, something is very wrong
            # at any point there should be buckets covering the whole space
            raise KeyError("Could not find a bucket for node_id: " + node.long_id)

        return search_result


table = RoutingTable()

for i in range(0, pow(2, 16)):
    key = os.urandom(20)  # 20 random bytes == 160 bits
    node = Node(("123.1.2." + str(i), 456), key)
    table.add_node(node)

print float(len(table.buckets[0].nodes)) / len(table.buckets[1].nodes)
