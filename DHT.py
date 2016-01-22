import logging
import os
import time

from KRPC import KRPCServer, BOOTSTRAP_NODE, build_find_node_krpc_query, build_ping_krpc_query
from RoutingTable import RoutingTable
from Swarm import Node
from bit_lib.bencode import decode_nodes


class DHT(object):
    def __init__(self):
        # Session key
        self._key = os.urandom(20)  # 20 random bytes == 160 bits
        self.krpc = KRPCServer(9001, "1.1.1")
        self.routing_table = RoutingTable()

    def ping_callback(self, message, connection):
        if "r" in message and "id" in message["r"]:
            message = message["r"]
            node_to_add = Node(connection, node_id=message["id"])
            self.routing_table.add_or_update_node(node_to_add)

    def find_node_callback(self, message, connection):
        if "r" in message and "nodes" in message["r"]:
            for node in decode_nodes(message["r"]["nodes"]):
                found_node = Node(node[1], node_id=node[0])
                self.krpc.send_query(build_ping_krpc_query(found_node.id), found_node, self.ping_callback)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    dht = DHT()
    dht.krpc.start()
    initial_ping_query = build_ping_krpc_query(dht._key)
    dht.krpc.send_query(initial_ping_query, BOOTSTRAP_NODE, dht.ping_callback)

    while True:
        items = dht.routing_table.find_node_or_closest_nodes(dht._key)

        for bucket in dht.routing_table.buckets:
            print(str(bucket) + " : " + str(bucket.nodes))

        if type(items) == Node:
            print "found ourselves!"
        else:
            for node_to_ask in items:
                self_discovery_query = build_find_node_krpc_query(dht._key, dht._key)
                dht.krpc.send_query(self_discovery_query, node_to_ask, dht.find_node_callback)
        time.sleep(5)
