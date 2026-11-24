import unittest

from orders import OrderService
from pg import FakePG


def setup(faults=(), seat_ok=True):
    pg = FakePG(); svc = OrderService(pg)
    svc.place(1, 18000, seat_ok)
    svc.checkout(1, faults)
    return pg, svc


class PaymentTest(unittest.TestCase):
    def test_timeout_after_charge_leaves_pending_until_webhook(self):
        pg, svc = setup(("timeout_after_charge",))
        self.assertEqual(svc.state(1), "PENDING")
        pg.deliver(svc.on_webhook)
        self.assertEqual(svc.state(1), "CONFIRMED")

    def test_duplicate_webhook_is_processed_once(self):
        pg, svc = setup(("timeout_after_charge", "duplicate_webhook"))
        got = []
        pg.deliver(lambda e: got.append(svc.on_webhook(e)))
        self.assertEqual(got, ["CONFIRMED", "중복 무시"])
        self.assertEqual(len(svc.audit(1)), 2)            # PENDING→PAID→CONFIRMED 한 번씩

    def test_retry_with_same_key_charges_once(self):
        pg, svc = setup(("timeout_after_charge", "lost_webhook"))
        svc.checkout(1)                                     # 손님이 다시 누름 → 같은 키
        self.assertEqual((len(pg.charges), svc.state(1)), (1, "CONFIRMED"))

    def test_lost_webhook_is_fixed_by_polling(self):
        pg, svc = setup(("timeout_after_charge", "lost_webhook"))
        pg.deliver(svc.on_webhook)
        self.assertEqual(svc.state(1), "PENDING")
        svc.poll()
        self.assertEqual(svc.state(1), "CONFIRMED")

    def test_reconcile_confirms_or_refunds_then_finds_nothing(self):
        pg = FakePG(); svc = OrderService(pg)
        for o, ok in ((1, True), (2, False)):
            svc.place(o, 18000, ok); svc.checkout(o, ("timeout_after_charge", "lost_webhook"))
        pg.lookup_down = True; svc.poll()
        self.assertEqual(len(svc.mismatches()), 2)
        self.assertEqual(svc.reconcile(), [(1, "CONFIRMED"), (2, "REFUNDED")])
        self.assertEqual(pg.charges["pay-2"]["status"], "refunded")
        self.assertEqual(svc.mismatches(), [])
        self.assertEqual(svc.reconcile(), [])               # 다시 돌려도 같은 결과

    def test_illegal_transition_is_refused(self):
        _, svc = setup()
        with self.assertRaises(AssertionError):
            svc.move(1, "CONFIRMED", "PENDING", "되돌리기")


if __name__ == "__main__":
    unittest.main()
