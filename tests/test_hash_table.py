import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hash_table import HashTable, horner_hash, horner_steps


def colliding_keys(m, count):
    """칸 수 m에서 같은 칸으로 가는 키를 count개 찾는다."""
    found = []
    target = horner_hash("k0", m)
    i = 0
    while len(found) < count:
        key = f"k{i}"
        if horner_hash(key, m) == target:
            found.append(key)
        i += 1
    return found


class TestHorner(unittest.TestCase):
    def test_empty_key(self):
        self.assertEqual(horner_hash("", 11), 0)

    def test_known_value(self):
        # "ab": h = 97 -> (31*97 + 98) mod 11
        self.assertEqual(horner_hash("ab", 11), (31 * (97 % 11) + 98) % 11)

    def test_range(self):
        for key in ("a", "hello", "https://example.com/x"):
            self.assertTrue(0 <= horner_hash(key, 13) < 13)

    def test_steps_end_at_hash(self):
        steps = horner_steps("abc", 11)
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[-1][-1], horner_hash("abc", 11))


class HashTableContract:
    """해시 테이블이라면 지켜야 하는 동작. 구현마다 make()만 바꿔 다시 돌린다."""

    def make(self, capacity=16, max_load=1.0):
        raise NotImplementedError

    def test_empty(self):
        t = self.make()
        self.assertEqual(len(t), 0)
        self.assertIsNone(t.get("x"))
        self.assertNotIn("x", t)
        self.assertEqual(t.load_factor(), 0)

    def test_put_get(self):
        t = self.make()
        t.put("a", 1)
        t.put("b", 2)
        self.assertEqual(t.get("a"), 1)
        self.assertEqual(t.get("b"), 2)
        self.assertIn("a", t)
        self.assertEqual(len(t), 2)

    def test_overwrite(self):
        t = self.make()
        t.put("a", 1)
        t.put("a", 9)
        self.assertEqual(t.get("a"), 9)
        self.assertEqual(len(t), 1)

    def test_empty_string_key(self):
        t = self.make()
        t.put("", "blank")
        self.assertEqual(t.get(""), "blank")

    def test_collisions(self):
        t = self.make(capacity=11, max_load=None)
        keys = colliding_keys(11, 4)
        for i, k in enumerate(keys):
            t.put(k, i)
        for i, k in enumerate(keys):
            self.assertEqual(t.get(k), i)
        self.assertEqual(len(t), 4)

    def test_find_reports_cost(self):
        t = self.make(capacity=11, max_load=None)
        t.put("a", 1)
        found, value, cost = t.find("a")
        self.assertTrue(found)
        self.assertEqual(value, 1)
        self.assertGreaterEqual(cost, 1)
        found, value, cost = t.find("zz-missing")
        self.assertFalse(found)
        self.assertIsNone(value)
        self.assertGreaterEqual(cost, 0)

    def test_load_factor(self):
        t = self.make(capacity=11, max_load=None)
        for i in range(5):
            t.put(f"key{i}", i)
        self.assertAlmostEqual(t.load_factor(), 5 / 11)

    def test_resize_keeps_everything(self):
        t = self.make(capacity=4)
        for i in range(500):
            t.put(f"https://example.com/{i}", i)
        self.assertGreater(t.capacity(), 4)
        self.assertEqual(len(t), 500)
        for i in range(500):
            self.assertEqual(t.get(f"https://example.com/{i}"), i)

    def test_no_resize_when_disabled(self):
        t = self.make(capacity=7, max_load=None)
        for i in range(5):
            t.put(f"k{i}", i)
        self.assertEqual(t.capacity(), 7)


class TestChainingHashTable(HashTableContract, unittest.TestCase):
    def make(self, capacity=16, max_load=1.0):
        return HashTable(capacity=capacity, max_load=max_load)

    def test_chaining_can_exceed_one(self):
        t = self.make(capacity=7, max_load=None)
        for i in range(20):
            t.put(f"k{i}", i)
        self.assertGreater(t.load_factor(), 1)
        for i in range(20):
            self.assertEqual(t.get(f"k{i}"), i)


if __name__ == "__main__":
    unittest.main()
