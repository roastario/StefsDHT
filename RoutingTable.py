# bep_0005 specifies to use the XOR Metric (ie, the distance between two nodes is the XOR value of their ids)
import math


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


# CONTRACT IS, IF COMPARATOR EVALUATES TO > 1, THE ITEM WE JUST ASKED ABOUT IS LARGER THAN THE ONE WE CURRIED IN
def fucksake_why_is_not_in_std_lib_search_for_item_with_custom_comparator(items, comparator, startIdx, endIdx):
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
            return fucksake_why_is_not_in_std_lib_search_for_item_with_custom_comparator(items, comparator,
                                                                                         new_start_idx, new_end_idx)
        elif comparison_result < 0:
            new_start_idx = startIdx
            new_end_idx = idx - 1

            return fucksake_why_is_not_in_std_lib_search_for_item_with_custom_comparator(items, comparator,
                                                                                         new_start_idx, new_end_idx)


class RoutingTable(object):
    MAX_NUMBER_OF_BUCKETS = int(pow(2, 16))

    def __init__(self):
        self.buckets = []


def curry_comparator(item_to_find, comparator):
    def curried(item_to_compare_to):
        return comparator(item_to_find, item_to_compare_to)

    return curried


items = []

for i in range(199999):
    items.append(i)

print fucksake_why_is_not_in_std_lib_search_for_item_with_custom_comparator(items, curry_comparator(302, lambda o1,
                                                                                                                o2: o1 - o2),
                                                                            0, len(items))
