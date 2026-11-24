import unittest

from log import hour
from signals import p99, pages, signals

ROWS = [signals(r) for r in hour()]


class GoldenTest(unittest.TestCase):
    def test_p99_nearest_rank(self):
        self.assertEqual(p99(list(range(1, 101))), 99)

    def test_db_slow_raises_latency_errors_saturation_and_dips_traffic(self):
        calm, slow = ROWS[20], ROWS[33]
        self.assertGreater(slow["p99_ok"], 5 * calm["p99_ok"])
        self.assertGreater(slow["err"], 10 * calm["err"])
        self.assertEqual(slow["sat"], 100)
        self.assertLess(slow["rps"], calm["rps"])

    def test_fast_500s_make_mixed_average_look_better(self):
        calm, cut = ROWS[20], ROWS[42]
        self.assertLess(cut["avg_all"], calm["avg_all"])
        self.assertGreater(cut["err"], 50)
        self.assertGreater(cut["avg_ok"], cut["avg_all"])

    def test_policy_errors_count_slow_successes(self):
        reqs = [(1500.0, 200, True), (50.0, 200, True), (50.0, 200, False), (3.0, 500, False)]
        self.assertEqual(signals(reqs)["err"], 75)

    def test_page_once_when_errors_stay_high(self):
        self.assertEqual(pages(ROWS), [31])


if __name__ == "__main__":
    unittest.main()
