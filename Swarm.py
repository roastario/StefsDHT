import math


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
    def __init__(self, address, node_id=None):
        self.address = address
        if node_id:
            self.id = node_id
            self.long_id = fucksake_why_isnt_this_std_lib_convert_eight_bit_string_to_number(node_id, 256)

    def __repr__(self):
        return "Node " + str(self.id) + " @ " + str(self.address)
