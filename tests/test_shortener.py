import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from base62 import decode
from hash_table import HashTable
from shortener import MAX_URL_LENGTH, Shortener


class ShortenerContract:
    """단축기 동작. 테이블 종류(table_cls)만 바꿔 다시 돌린다."""

    table_cls = None

    def make(self):
        return Shortener(table_cls=self.table_cls)

    def test_round_trip(self):
        s = self.make()
        code = s.shorten("https://example.com/a")
        self.assertEqual(s.expand(code), "https://example.com/a")

    def test_same_url_same_code(self):
        s = self.make()
        a = s.shorten("https://example.com/a")
        b = s.shorten("https://example.com/a")
        self.assertEqual(a, b)
        self.assertEqual(len(s), 1)

    def test_different_urls_different_codes(self):
        s = self.make()
        a = s.shorten("https://example.com/a")
        b = s.shorten("https://example.com/b")
        self.assertNotEqual(a, b)

    def test_codes_are_serial_numbers(self):
        s = self.make()
        codes = [s.shorten(f"https://example.com/{i}") for i in range(3)]
        self.assertEqual([decode(c) for c in codes], [1, 2, 3])

    def test_unknown_code(self):
        s = self.make()
        self.assertIsNone(s.expand("abc"))
        self.assertIsNone(s.expand("!!"))

    def test_strip_spaces(self):
        s = self.make()
        a = s.shorten("  https://example.com/a  ")
        self.assertEqual(s.expand(a), "https://example.com/a")

    def test_http_allowed(self):
        s = self.make()
        self.assertEqual(s.expand(s.shorten("http://example.com")), "http://example.com")

    def test_bad_urls(self):
        s = self.make()
        bad = [
            "",
            "   ",
            "ftp://example.com/file",
            "javascript:alert(1)",
            "example.com",
            "http://",
            "https://exa mple.com",
            "https://example.com/" + "a" * MAX_URL_LENGTH,
            None,
        ]
        for url in bad:
            with self.assertRaises(ValueError, msg=repr(url)):
                s.shorten(url)
        self.assertEqual(len(s), 0)

    def test_many_urls(self):
        s = self.make()
        codes = [s.shorten(f"https://example.com/page/{i}") for i in range(1000)]
        for i, code in enumerate(codes):
            self.assertEqual(s.expand(code), f"https://example.com/page/{i}")


class TestShortenerChaining(ShortenerContract, unittest.TestCase):
    table_cls = HashTable


if __name__ == "__main__":
    unittest.main()
