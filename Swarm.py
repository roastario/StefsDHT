import math
import time


def fucksake_why_isnt_this_std_lib_convert_eight_bit_string_to_number(string, base):
    # assume big endian
    value = 0
    power = len(string) - 1
    for character in string:

        if ord(character) >= base:
            raise ArithmeticError("Encountered value: " + str(character) +
                                  " which is larger than " + str(base))

        value_of_this_index = math.pow(base, power) * ord(character)
        value += value_of_this_index

        power -= 1
    return long(value)


class Node(object):
    NUMBER_OF_SECONDS_IN_15_MIN = 60 * 15

    def __init__(self, address, node_id=None, long_id=None):
        self.address = address
        if node_id:
            self.id = node_id
        if not long_id and node_id:
            self.long_id = fucksake_why_isnt_this_std_lib_convert_eight_bit_string_to_number(node_id, 256)
        if long_id or long_id == 0:
            self.long_id = long_id
        self.time_seen = int(time.time())

    def is_good(self):
        return (time.time() - self.time_seen) < Node.NUMBER_OF_SECONDS_IN_15_MIN

    def update_last_seen(self):
        self.time_seen = int(time.time())

    def __repr__(self):
        return "Node " + str(self.long_id) + " @ " + str(self.address)
