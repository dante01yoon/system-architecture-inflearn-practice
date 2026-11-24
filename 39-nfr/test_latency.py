import unittest

from latency import chance_slow, histogram, page_times, percentile, sample, summary


class LatencyTest(unittest.TestCase):
    def test_percentile_nearest_rank(self):
        ms = list(range(1, 101))
        self.assertEqual((percentile(ms, 50), percentile(ms, 99), percentile(ms, 100)), (50, 99, 100))

    def test_tail_pulls_mean_above_median(self):
        s = summary(sample())
        self.assertGreater(s["평균"], s["p50"])
        self.assertLess(s["p50"], s["p95"])
        self.assertLess(s["p95"], s["p99"])
        self.assertLess(s["p99"], s["p99.9"])

    def test_histogram_counts_everything(self):
        ms = sample(2_000)
        self.assertEqual(sum(c for _, c, _ in histogram(ms)), 2_000)

    def test_fanout_matches_one_minus_099_to_the_n(self):
        self.assertAlmostEqual(chance_slow(10), 1 - 0.99 ** 10)
        p99 = percentile(sample(200_000, 1), 99)
        pages = page_times(10, n=5_000)
        self.assertAlmostEqual(sum(t > p99 for t in pages) / len(pages), chance_slow(10), delta=0.02)


if __name__ == "__main__":
    unittest.main()
