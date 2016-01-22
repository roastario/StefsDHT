from unittest import TestCase

from RoutingTable import Bucket
from Swarm import Node


class TestBucket(TestCase):
    def test_add_node(self):
        bucket = Bucket(0, 10)

        node = Node(None, long_id=5)
        bucket.add_node(node)

        assert node in bucket.nodes

    def test_find_node_in_bucket(self):
        bucket = Bucket(0, 10)
        node1 = Node(None, long_id=1)
        node2 = Node(None, long_id=2)
        node3 = Node(None, long_id=3)
        bucket.add_node(node1)
        bucket.add_node(node2)
        bucket.add_node(node3)

        found_node = bucket.find_node_in_bucket(node1)

        assert found_node
        assert found_node == node1

    def test_split_into_two_buckets(self):

        bucket = Bucket(0, 99)

        for i in xrange(0, 100):
            node_to_add = Node(None, long_id=i)
            bucket.add_node(node_to_add)

        lower_half, upper_half = bucket.split_into_two_nodes_with_half_the_id_space()

        assert lower_half.max_id == 49
        assert lower_half.min_id == 0

        assert upper_half.max_id == 99
        assert upper_half.min_id == 50

        assert len(lower_half.nodes) == 50
        assert len(upper_half.nodes) == 50

        for node in lower_half.nodes:
            self.assertLessEqual(node.long_id, lower_half.max_id)
            self.assertGreaterEqual(node.long_id, lower_half.min_id)

        for node in upper_half.nodes:
            self.assertLessEqual(node.long_id, upper_half.max_id)
            self.assertGreaterEqual(node.long_id, upper_half.min_id)

        low, high = upper_half.split_into_two_nodes_with_half_the_id_space()

        assert low.min_id == upper_half.min_id
        self.assertLessEqual(low.max_id, upper_half.min_id + (upper_half.max_id - upper_half.min_id) // 2)

        assert high.min_id == upper_half.min_id + (upper_half.max_id - upper_half.min_id) // 2 + 1
        assert high.max_id == upper_half.max_id
