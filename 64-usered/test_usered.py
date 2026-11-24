import unittest

from methods import p99, red, suspicious, use
from metrics import seconds

LOG = seconds()


class UseRedTest(unittest.TestCase):
    def test_p99_nearest_rank(self):
        self.assertEqual(p99(list(range(1, 101))), 99)

    def test_red_finds_checkout_errors_and_duration_up_rate_same(self):
        before, now = red(LOG[:300]), red(LOG[300:])
        r0, e0, d0 = before["/checkout"]
        r1, e1, d1 = now["/checkout"]
        self.assertAlmostEqual(r0, r1, delta=0.5)
        self.assertGreater(e1, 5)
        self.assertGreater(d1, 10 * d0)
        for ep in ("/books", "/search", "/cart"):
            self.assertLess(now[ep][1], 1)

    def test_use_flags_only_the_pool(self):
        now = use(LOG[300:])
        flagged = [n for n, v in now.items() if suspicious(*v)]
        self.assertEqual(flagged, ["DB 연결 풀"])
        self.assertGreater(now["DB 연결 풀"][1], 0)
        self.assertLess(now["앱 CPU"][0], 70)

    def test_suspicious_rules(self):
        self.assertTrue(suspicious(75, 0, 0))
        self.assertTrue(suspicious(10, 1, 0))
        self.assertTrue(suspicious(10, 0, 1))
        self.assertFalse(suspicious(69, 0, 0))

    def test_releasing_connection_before_payment_fixes_pool(self):
        fixed = seconds(hold_while_paying=False)
        self.assertLess(use(fixed[300:])["DB 연결 풀"][0], 10)
        self.assertEqual(red(fixed[300:])["/checkout"][1], 0)


if __name__ == "__main__":
    unittest.main()
