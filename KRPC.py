import logging
import os
import socket
import struct
import threading
import time

from  Swarm import Node
from bit_lib.bencode import bencode, bdecode

LOGGER = logging.getLogger(__name__)

BOOTSTRAP_NODE = Node((socket.gethostbyaddr("router.bittorrent.com")[2][0], 6881))


def build_ping_krpc_query(id_):
    return {"y": "q", "q": "ping", "a": {"id": id_}}


def build_find_node_krpc_query(id_, target):
    return {"y": "q", "q": "find_node", "a": {"id": id_, "target": target}}


def build_get_peers_krpc_query(id_, info_hash):
    return {"y": "q", "q": "get_peers", "a": {"id": id_, "info_hash": info_hash}}


class KRPCServer(object):
    def __init__(self, port, version):
        self._port = port
        self._version = version
        self._shutdown_flag = False
        self._thread = None
        self.sock = None
        self._transaction_id = 0
        self._transactions = {}
        self._transactions_lock = threading.Lock()
        self._results = {}
        self.reply_handler = self.default_handler
        self.query_handler = self.default_handler
        self._key = os.urandom(20)  # 20 random bytes == 160 bits

    def default_handler(self, message):
        if message["t"] in self._transactions:
            self._transactions[message["t"]][0](message)
        else:
            LOGGER.info("Received: " + str(message))

        # do a little bit of house keeping
        for _transaction_id in self._transactions.keys():
            _transaction = self._transactions[_transaction_id]
            if time.time() - _transaction[1] > 30:
                del self._transactions[_transaction_id]

    def start(self):
        LOGGER.info("Starting KRPC Server")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(0.5)
        self.sock.bind(("0.0.0.0", self._port))
        self._thread = threading.Thread(target=self.keep_alive)
        self._thread.daemon = True
        self._thread.start()

    def keep_alive(self):
        while True:
            try:
                if self._shutdown_flag:
                    break
                received_data, c = self.sock.recvfrom(4096)
                LOGGER.debug("Received data from %r", c)
                decoded_data = bdecode(received_data)

                if "y" in decoded_data and decoded_data["y"] == "r":
                    # this is a reply
                    self.reply_handler(message=decoded_data)
                else:
                    # this is a query directed to us
                    pass

            except socket.timeout:
                LOGGER.info("nothing was received")

    def generate_transaction_id(self):
        self._transaction_id += 1
        return struct.pack("i", self._transaction_id)

    def send_query(self, query, target_node, callback=None):
        # for testing, enforce a 1sec between requests
        time.sleep(1)
        transaction_id = self.generate_transaction_id()
        query["t"] = transaction_id
        query["v"] = self._version
        data = bencode(query)
        if callback:
            self._transactions[transaction_id] = (callback, time.time())
        self.sock.sendto(data, target_node.address)
