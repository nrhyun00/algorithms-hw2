import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from hash_table import horner_hash
from probing_table import LinearProbingTable
from test_hash_table import HashTableContract


def keys_with_home(m, home, count):
    found = []
    i = 0
    while len(found) < count:
        key = f"w{i}"
        if horner_hash(key, m) == home:
            found.append(key)
        i += 1
    return found


class TestLinearProbingTable(HashTableContract, unittest.TestCase):
    """체이닝 테이블과 같은 테스트를 선형 탐지에도 돌린다."""

    def make(self, capacity=16, max_load=0.5):
        return LinearProbingTable(capacity=capacity, max_load=max_load)


class TestLinearProbingOnly(unittest.TestCase):
    def test_wraps_from_last_slot_to_zero(self):
        m = 11
        t = LinearProbingTable(capacity=m, max_load=None)
        a, b, c = keys_with_home(m, m - 1, 3)
        for i, k in enumerate((a, b, c)):
            t.put(k, i)
        slots = t.slots()
        self.assertEqual(slots[m - 1][0], a)
        self.assertEqual(slots[0][0], b)
        self.assertEqual(slots[1][0], c)
        self.assertEqual(t.get(c), 2)
        self.assertEqual(t.find(c)[2], 3)
        self.assertEqual(slots[1][3], 3)

    def test_full_table(self):
        m = 7
        t = LinearProbingTable(capacity=m, max_load=None)
        for i in range(m):
            t.put(f"k{i}", i)
        self.assertEqual(len(t), m)
        self.assertEqual(t.load_factor(), 1)
        for i in range(m):
            self.assertEqual(t.get(f"k{i}"), i)
        found, value, looked = t.find("not-here")
        self.assertFalse(found)
        self.assertIsNone(value)
        self.assertEqual(looked, m)
        self.assertNotIn("not-here", t)
        t.put("k3", 99)
        self.assertEqual(t.get("k3"), 99)
        self.assertEqual(len(t), m)
        self.assertEqual(t.capacity(), m)

    def test_full_table_grows_on_new_key(self):
        m = 7
        t = LinearProbingTable(capacity=m, max_load=None)
        for i in range(m):
            t.put(f"k{i}", i)
        t.put("one-more", 0)
        self.assertGreater(t.capacity(), m)
        self.assertEqual(len(t), m + 1)
        self.assertEqual(t.get("one-more"), 0)
        for i in range(m):
            self.assertEqual(t.get(f"k{i}"), i)

    def test_miss_counts_the_empty_slot(self):
        t = LinearProbingTable(capacity=11, max_load=None)
        self.assertEqual(t.find("x"), (False, None, 1))

    def test_cluster_cost(self):
        m = 11
        t = LinearProbingTable(capacity=m, max_load=None)
        keys = keys_with_home(m, 4, 4)
        for k in keys:
            t.put(k, True)
        for n, k in enumerate(keys, start=1):
            self.assertEqual(t.find(k)[2], n)

    def test_resize_keeps_load_low(self):
        t = LinearProbingTable(capacity=4, max_load=0.5)
        for i in range(200):
            t.put(f"u{i}", i)
            self.assertLessEqual(t.load_factor(), 0.5)


if __name__ == "__main__":
    unittest.main()
