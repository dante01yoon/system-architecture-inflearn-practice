import unittest

from sim import N, arrivals, queue_length, simulate


class LoadLevel(unittest.TestCase):
    def test_same_seed_same_story(self):
        self.assertEqual(arrivals(), arrivals())
        self.assertEqual(simulate(300)["done"], simulate(300)["done"])

    def test_every_order_is_either_done_or_rejected(self):
        for limit in (0, 300, None):
            r = simulate(limit)
            self.assertEqual(r["done"] + r["rejected"], N)

    def test_direct_drops_orders_without_waiting(self):
        r = simulate(0)
        self.assertGreater(r["rejected"], 0)
        self.assertAlmostEqual(r["max_wait"], 0.0)

    def test_unbounded_queue_takes_all_but_waits_long(self):
        r = simulate(None)
        self.assertEqual(r["rejected"], 0)
        self.assertGreater(r["max_wait"], 9)
        self.assertGreater(r["end"], 19)

    def test_bounded_queue_caps_wait_by_littles_law(self):
        r = simulate(300)  # 100건/초 × 3초
        self.assertGreater(r["rejected"], 0)
        self.assertLessEqual(r["max_wait"], 3.0 + 0.04)
        self.assertLessEqual(max(queue_length(r["starts"], t / 2) for t in range(44)), 300)


if __name__ == "__main__":
    unittest.main()
