import unittest

from breaker import CircuitBreaker
from review import Clock, ReviewService

FB = lambda: "fallback"  # noqa: E731


class BreakerTest(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.svc = ReviewService(self.clock)
        self.b = CircuitBreaker(threshold=3, reset_timeout=4, clock=self.clock)

    def test_opens_after_threshold_failures(self):
        self.svc.down = True
        for _ in range(2):
            self.b.call(self.svc.get, FB)
        self.assertEqual(self.b.state, "closed")
        self.b.call(self.svc.get, FB)
        self.assertEqual(self.b.state, "open")

    def test_open_fails_fast_without_calling(self):
        self.svc.down = True
        for _ in range(3):
            self.b.call(self.svc.get, FB)
        calls, now = self.svc.calls, self.clock()
        self.assertEqual(self.b.call(self.svc.get, FB), "fallback")
        self.assertEqual((self.svc.calls, self.clock()), (calls, now))

    def test_half_open_probe_success_closes(self):
        self.svc.down = True
        for _ in range(3):
            self.b.call(self.svc.get, FB)
        self.clock.wait(4)
        self.svc.down = False
        self.assertEqual(self.b.call(self.svc.get, FB), "별점 4.6 (128개)")
        self.assertEqual((self.b.state, self.b.failures), ("closed", 0))

    def test_half_open_probe_failure_reopens_and_restarts_timer(self):
        self.svc.down = True
        for _ in range(3):
            self.b.call(self.svc.get, FB)
        self.clock.wait(4)
        self.b.call(self.svc.get, FB)
        self.assertEqual(self.b.state, "open")
        self.assertEqual(self.b.opened_at, self.clock())

    def test_success_resets_failure_count(self):
        self.svc.down = True
        self.b.call(self.svc.get, FB), self.b.call(self.svc.get, FB)
        self.svc.down = False
        self.b.call(self.svc.get, FB)
        self.assertEqual(self.b.failures, 0)


if __name__ == "__main__":
    unittest.main()
