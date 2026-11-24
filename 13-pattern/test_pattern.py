import unittest

import cache_aside
import read_through
from demo import NoCache, run


class PatternTest(unittest.TestCase):
    def test_no_cache_calls_every_time(self):
        self.assertEqual(run(NoCache), (20, 0))

    def test_cache_aside_invalidates_on_write(self):
        self.assertEqual(run(lambda r, c: cache_aside.Shop(r)), (3, 0))

    def test_cache_aside_forgetting_invalidation_serves_old_price(self):
        self.assertEqual(run(lambda r, c: cache_aside.Shop(r, forget=True)), (2, 7))

    def test_read_through_trades_staleness_for_calls(self):
        self.assertEqual(run(lambda r, c: read_through.Shop(r, 10, c)), (4, 2))
        self.assertEqual(run(lambda r, c: read_through.Shop(r, 4, c)), (10, 1))


if __name__ == "__main__":
    unittest.main()
