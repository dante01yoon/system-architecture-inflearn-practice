import unittest

from limiters import FixedWindow, LeakyBucket, SlidingCounter, SlidingLog, TokenBucket
from store import Store, check_then_set, incr_then_check


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def run(lim, clock, times):
    out = []
    for t in times:
        clock.t = t
        out.append(lim.allow())
    return out


class LimiterTest(unittest.TestCase):
    def test_fixed_window_doubles_at_boundary(self):
        c = Clock()
        r = run(FixedWindow(3, 10, c), c, [9, 9, 9, 9, 10, 10, 10, 10])
        self.assertEqual(sum(r), 6)          # 9초와 10초 사이 1초에 6개

    def test_sliding_log_holds_limit_in_any_window(self):
        c = Clock()
        r = run(SlidingLog(3, 10, c), c, [9, 9, 9, 10, 10, 19.5, 20])
        self.assertEqual(r, [True, True, True, False, False, True, True])

    def test_sliding_counter_weights_previous_window(self):
        c = Clock()
        lim = SlidingCounter(10, 60, c)
        run(lim, c, [30] * 10)               # 앞 칸 10개
        c.t = 75                             # 앞 칸이 75% 겹침 → 7.5
        self.assertEqual(sum(run(lim, c, [75] * 5)), 3)

    def test_token_bucket_refills_and_caps(self):
        c = Clock()
        tb = TokenBucket(2, 1, c)
        self.assertEqual(run(tb, c, [0, 0, 0]), [True, True, False])
        self.assertEqual(tb.retry_after(), 1)
        c.t = 100
        self.assertEqual(sum(run(tb, c, [100, 100, 100])), 2)

    def test_leaky_bucket_drains(self):
        c = Clock()
        lb = LeakyBucket(2, 0.5, c)
        self.assertEqual(run(lb, c, [0, 0, 0, 2, 2]), [True, True, False, True, False])


class RaceTest(unittest.TestCase):
    def test_get_then_set_over_admits(self):
        self.assertEqual(check_then_set(Store(), "k", 10, 20), 20)
        self.assertEqual(incr_then_check(Store(), "k", 10, 20), 10)


if __name__ == "__main__":
    unittest.main()
