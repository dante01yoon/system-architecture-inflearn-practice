import random
import threading
import unittest

from cache import LRU, Origin, early, jitter_ttl, read, read_once, zipf_keys


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class LRUTest(unittest.TestCase):
    def test_evicts_least_recently_used(self):
        c = LRU(2)
        c.put("a", 1); c.put("b", 2)
        c.get("a")                    # a를 썼다 → b가 가장 오래 안 씀
        c.put("c", 3)
        self.assertIsNone(c.get("b"))
        self.assertEqual((c.get("a"), c.get("c")), (1, 3))

    def test_ttl_expires(self):
        clock = Clock()
        c = LRU(10, ttl=60, clock=clock)
        c.put("k", "v")
        clock.t = 59.9
        self.assertEqual(c.get("k"), "v")
        clock.t = 60
        self.assertIsNone(c.get("k"))

    def test_bigger_cache_hits_more(self):
        reqs = zipf_keys(1_000, 20_000)
        ratios = []
        for size in (10, 100, 500):
            c = LRU(size)
            for k in reqs:
                if c.get(k) is None:
                    c.put(k, k)
            ratios.append(c.ratio())
        self.assertEqual(ratios, sorted(ratios))


class StampedeTest(unittest.TestCase):
    def run_100(self, fn):
        cache, origin = LRU(10), Origin(delay=0.2)
        b = threading.Barrier(100)
        ts = [threading.Thread(target=lambda: (b.wait(), fn(cache, origin, "hot"))) for _ in range(100)]
        [t.start() for t in ts]; [t.join() for t in ts]
        return origin.calls

    def test_single_flight_calls_origin_once(self):
        self.assertEqual(self.run_100(read_once), 1)

    def test_plain_read_stampedes(self):
        self.assertGreater(self.run_100(read), 50)


class ExpiryTest(unittest.TestCase):
    def test_jitter_stays_in_range(self):
        rnd = random.Random(1)
        vals = [jitter_ttl(60, 0.1, rnd) for _ in range(1000)]
        self.assertTrue(all(54 <= v <= 66 for v in vals))

    def test_early_more_likely_near_expiry(self):
        rnd = random.Random(1)
        far = sum(early(0, 100, delta=1, rnd=rnd) for _ in range(2000))
        near = sum(early(99, 100, delta=1, rnd=rnd) for _ in range(2000))
        self.assertLess(far, near)
        self.assertEqual(early(100, 100, delta=1, rnd=rnd), True)


if __name__ == "__main__":
    unittest.main()
