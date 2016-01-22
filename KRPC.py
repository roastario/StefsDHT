import logging
import os
import socket
import struct
import threading
import time

from  Swarm import Node
from bit_lib.BTL import BTFailure
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

    def default_handler(self, message=None, connection=None):
        if message is None:
            message = {}
        if message["t"]:
            transaction_id = self.decode_transaction_id(message["t"])
            if transaction_id:
                try:
                    callback, time_registered = self.get_callback_for_transaction_id(transaction_id)
                    callback(message, connection)
                except KeyError:
                    print "could not find a handler for transaction_id " + str(transaction_id)
        else:
            # print(str(message) + " is missing transaction_id ")
            pass

        # do a little bit of house keeping
        for _transaction_id in self._transactions.keys():
            _transaction = self._transactions[_transaction_id]
            if time.time() - _transaction[1] > 30:
                del self._transactions[_transaction_id]

    def get_callback_for_transaction_id(self, transaction_id):
        callback_holder = self._transactions[transaction_id]
        del self._transactions[transaction_id]
        return callback_holder[0], callback_holder[1]

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
                decoded_data = bdecode(received_data)
                if "y" in decoded_data and decoded_data["y"] == "r":
                    # this is a reply
                    self.reply_handler(message=decoded_data, connection=c)
                else:
                    # this is a query directed to us
                    # print(str(decoded_data) + " is unhandled ")
                    pass

            except socket.timeout:
                LOGGER.info("nothing was received")
            except BTFailure:
                print "Invalid bencoded string: " + received_data

    def generate_transaction_id(self):
        self._transaction_id += 1
        return struct.pack("i", self._transaction_id), self._transaction_id

    @staticmethod
    def decode_transaction_id(packed_transaction):
        try:
            unpack = struct.unpack("i", packed_transaction)
        except:
            # print "misformed reponse transaction id: " + packed_transaction
            unpack = (None, None)
        return unpack[0]

    def send_query(self, query, target_node, callback=None):
        # for testing, enforce a 1sec between requests
        transaction_id_packed, transaction_id_int = self.generate_transaction_id()
        query["t"] = transaction_id_packed
        query["v"] = self._version
        data = bencode(query)
        if callback:
            self._transactions[transaction_id_int] = (callback, time.time())
        self.sock.sendto(data, target_node.address)
