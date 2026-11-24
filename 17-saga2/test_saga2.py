import unittest

from demo import choreo, orches


class Saga2Test(unittest.TestCase):
    def test_both_styles_succeed(self):
        bus, shop = choreo({"id": 1, "book": "DDIA", "qty": 1})
        self.assertEqual((shop.orders[1], shop.stock["DDIA"], shop.shipped), ("APPROVED", 2, [1]))
        saga, shop = orches({"id": 1, "book": "DDIA", "qty": 1})
        self.assertEqual((shop.orders[1], shop.stock["DDIA"], shop.shipped), ("APPROVED", 2, [1]))

    def test_payment_failure_rejects_order_in_both(self):
        bad = {"id": 3, "book": "DDIA", "qty": 1, "card": "거절"}
        for _, shop in (choreo(dict(bad)), orches(dict(bad))):
            self.assertEqual((shop.orders[3], shop.stock["DDIA"], shop.paid), ("REJECTED", 3, {}))

    def test_stock_failure_refunds_payment_in_both(self):
        big = {"id": 4, "book": "DDIA", "qty": 9}
        for _, shop in (choreo(dict(big)), orches(dict(big))):
            self.assertEqual((shop.orders[4], shop.paid[4], shop.stock["DDIA"]), ("REJECTED", "REFUNDED", 3))

    def test_orchestrator_retries_step_after_pivot(self):
        saga, shop = orches({"id": 2, "book": "DDIA", "qty": 1}, flaky=2)
        self.assertEqual(saga.log.count("배송 다시 시도 (배송사 응답 없음)"), 2)
        self.assertEqual(shop.orders[2], "APPROVED")


if __name__ == "__main__":
    unittest.main()
