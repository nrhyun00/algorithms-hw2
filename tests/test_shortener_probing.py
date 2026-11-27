import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from probing_table import LinearProbingTable
from test_shortener import ShortenerContract


class TestShortenerLinearProbing(ShortenerContract, unittest.TestCase):
    """단축기 테스트를 선형 탐지 테이블로 다시 돌린다."""

    table_cls = LinearProbingTable


if __name__ == "__main__":
    unittest.main()
