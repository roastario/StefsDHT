import logging
import os
import time

from KRPC import KRPCServer, build_get_peers_krpc_query, BOOTSTRAP_NODE, build_ping_krpc_query, \
    build_find_node_krpc_query
from Swarm import Node
from bit_lib.bencode import decode_nodes


class DHT(object):
    def __init__(self, target_hash):
        # Session key
        self._key = os.urandom(20)  # 20 random bytes == 160 bits
        self.krpc = KRPCServer(9001, "1.1.1")
        self.target_hash = target_hash

        pass

    def build_handle_get_peers_callback(self):

        def print_nodes(message):
            if "r" in message and "nodes" in message["r"]:
                nodes = decode_nodes(message["r"]["nodes"])
                for node in nodes:
                    found_node = Node(node[1], node_id=node[0])
                    print "Created: " + str(found_node)
                    get_nodes_query = build_find_node_krpc_query(self._key, self._key)
                    self.krpc.send_query(get_nodes_query, found_node, print_nodes)

        return print_nodes


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    dht = DHT("02b4c27f899425b67737cbec18eaedf1b9343d3b")
    dht.krpc.start()
    query = build_find_node_krpc_query(dht._key, dht._key)
    dht.krpc.send_query(query, BOOTSTRAP_NODE, dht.build_handle_get_peers_callback())

    while True:
        time.sleep(1)
