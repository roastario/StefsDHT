import math
import random
import string


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
        self.bucket_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    def has_capacity(self):
        return len(self.nodes) < Bucket.CAPACITY

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

    def split_into_two_nodes_with_half_the_id_space(self):
        # modify old bucket to have half the id space
        # create new bucket with the upper half we just removed

        mid_point = self.min_id + ((self.max_id - self.min_id) // 2)

        new_bucket_1 = Bucket(self.min_id, mid_point)
        new_bucket_2 = Bucket(mid_point + 1, self.max_id)

        # print "split: " + str(self) + " into : " + str(new_bucket_1) +" and " + str(new_bucket_2)
        old_nodes = self.nodes
        self.nodes = []

        for old_node in old_nodes:
            comparator = Bucket.build_comparator_for_node(old_node.long_id)
            if comparator(new_bucket_1) == 0:
                # option is either we fit, or we go into the new bucket
                new_bucket_1.add_node(old_node)
            else:
                new_bucket_2.add_node(old_node)

        return new_bucket_1, new_bucket_2

    def __repr__(self):
        return "bucket@" + self.bucket_id + " " + str(self.min_id) + "->" + str(self.max_id)


class RoutingTable(object):
    MAX_NUMBER_OF_BUCKETS = int(pow(2, 16))
    MAX_ID = long(pow(2, 160)) - 1
    MIN_ID = 0

    def __init__(self):
        self.buckets = [Bucket(RoutingTable.MIN_ID, RoutingTable.MAX_ID)]

    def add_node(self, node_to_add):
        search_result = self.find_node_bucket(node_to_add)
        bucket = search_result[0]

        if bucket.has_capacity():
            bucket.add_node(node_to_add)
        else:
            lower_half_bucket, upper_half_bucket = bucket.split_into_two_nodes_with_half_the_id_space()
            idx_to_replace = search_result[1]
            self.buckets[idx_to_replace] = lower_half_bucket
            self.buckets.insert(idx_to_replace + 1, upper_half_bucket)

    def find_node_bucket(self, node_to_find):
        search_result = fucksake_why_isnt_this_std_lib_search_sorted_list(self.buckets,
                                                                          Bucket.build_comparator_for_node(
                                                                                  node_to_find.long_id),
                                                                          0, len(self.buckets) - 1)
        found_bucket = search_result[0]
        if not found_bucket:
            # we did not find a bucket, something is very wrong
            # at any point there should be buckets covering the whole space
            raise KeyError("Could not find a bucket for node_id: " + str(node_to_find.long_id))

        return search_result
