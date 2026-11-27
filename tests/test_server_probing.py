import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from test_server import ServerContract


class TestServerLinearProbing(ServerContract, unittest.TestCase):
    """서버 테스트를 선형 탐지 테이블로 다시 돌린다."""

    table = "probing"

    def test_table_shows_probe_count(self):
        self.shorten("https://example.com/a")
        resp, body = self.request("GET", "/table")
        self.assertIn("probing", body)
        self.assertIn("처음 칸", body)
        self.assertIn("칸을 봄", body)


if __name__ == "__main__":
    unittest.main()
