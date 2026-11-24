import unittest

from sim import run


class SimTest(unittest.TestCase):
    def test_same_seed_same_result(self):
        self.assertEqual(run(5), run(5))

    def test_monolith_has_no_network_cost(self):
        r = run(0)
        self.assertAlmostEqual(r["avg"], 0.05)
        self.assertEqual(r["fail"], 0.0)

    def test_more_calls_more_latency_and_failures(self):
        r2, r5, r10 = run(2), run(5), run(10)
        self.assertLess(r2["avg"], r5["avg"])
        self.assertLess(r5["avg"], r10["avg"])
        self.assertLess(r2["fail"], r10["fail"])
        self.assertAlmostEqual(r10["fail"], 1 - 0.999 ** 10, delta=0.004)

    def test_parallel_calls_wait_for_the_slowest_only(self):
        self.assertLess(run(5, parallel=True)["avg"], run(5)["avg"])
        self.assertEqual(run(5, parallel=True)["fail"], run(5)["fail"])


if __name__ == "__main__":
    unittest.main()
