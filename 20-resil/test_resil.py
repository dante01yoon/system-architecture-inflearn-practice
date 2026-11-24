import random
import time
import unittest

from bulkhead import bulkheads, call_with_timeout, shared_pool
from demo import order_wait
from payment import PaymentServer
from retry import backoff, retry
from services import Review
from storm import simulate


class BulkheadTest(unittest.TestCase):
    def test_slow_review_starves_shared_pool_but_not_bulkhead(self):
        review = Review()
        review.slow = True
        self.assertGreater(order_wait(shared_pool(4), review), 1.5)
        self.assertLess(order_wait(bulkheads({"review": 2, "order": 2}), review), 0.5)

    def test_timeout_returns_fallback(self):
        review = Review()
        review.slow = True
        start = time.time()
        self.assertEqual(call_with_timeout(bulkheads({"r": 1})["r"].submit(review.get), 0.2, "fb"), "fb")
        self.assertLess(time.time() - start, 0.5)


class RetryTest(unittest.TestCase):
    def test_backoff_doubles_and_caps(self):
        self.assertEqual([backoff(a) for a in range(5)], [1, 2, 4, 8, 8])
        rng = random.Random(0)
        self.assertTrue(all(0 <= backoff(a, rng=rng) <= min(8, 2 ** a) for a in range(10)))

    def test_jitter_spreads_retries(self):
        plain, jit = simulate(False), simulate(True)
        self.assertEqual(plain[0], 100)
        self.assertLess(jit[0], plain[0])
        self.assertLess(jit[2], plain[2])

    def test_retry_gives_up(self):
        def boom():
            raise ConnectionError
        with self.assertRaises(ConnectionError):
            retry(boom, 3, None, lambda s: None)


class IdempotencyTest(unittest.TestCase):
    def pay(self, key):
        server = PaymentServer()
        server.lose_reply = 1
        reply = retry(lambda: server.charge("o", 18000, key), 3, None, lambda s: None)
        return reply, server.total("o")

    def test_no_key_double_charges(self):
        self.assertEqual(self.pay(None)[1], (2, 36000))

    def test_key_charges_once_and_returns_first_reply(self):
        reply, total = self.pay("k")
        self.assertEqual((reply["charge"], total), (1, (1, 18000)))

    def test_same_key_different_request_is_rejected(self):
        server = PaymentServer()
        server.charge("o", 18000, "k")
        with self.assertRaises(ValueError):
            server.charge("o", 99000, "k")


if __name__ == "__main__":
    unittest.main()
