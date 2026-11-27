import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from base62 import decode, encode


class TestEncode(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(encode(0), "0")

    def test_single_digits(self):
        self.assertEqual(encode(9), "9")
        self.assertEqual(encode(10), "a")
        self.assertEqual(encode(35), "z")
        self.assertEqual(encode(36), "A")
        self.assertEqual(encode(61), "Z")

    def test_two_digits(self):
        self.assertEqual(encode(62), "10")
        self.assertEqual(encode(62 * 62 - 1), "ZZ")
        self.assertEqual(encode(62 * 62), "100")

    def test_negative(self):
        with self.assertRaises(ValueError):
            encode(-1)

    def test_not_int(self):
        for bad in (1.5, "3", None, True):
            with self.assertRaises(TypeError):
                encode(bad)


class TestDecode(unittest.TestCase):
    def test_known(self):
        self.assertEqual(decode("0"), 0)
        self.assertEqual(decode("Z"), 61)
        self.assertEqual(decode("10"), 62)

    def test_leading_zero(self):
        self.assertEqual(decode("010"), 62)

    def test_bad_char(self):
        for bad in ("a-b", " ", "가", "ab!"):
            with self.assertRaises(ValueError):
                decode(bad)

    def test_empty(self):
        with self.assertRaises(ValueError):
            decode("")

    def test_round_trip(self):
        for n in list(range(0, 5000)) + [10**12, 2**63]:
            self.assertEqual(decode(encode(n)), n)

    def test_case_sensitive(self):
        self.assertNotEqual(decode("a"), decode("A"))


if __name__ == "__main__":
    unittest.main()
