import unittest

from clock import MonotonicClock, WallClock, lww_merge
from lock import LockService, Storage
from net import PaymentServer, call


class TroubleTest(unittest.TestCase):
    def test_client_cannot_tell_lost_request_from_lost_response(self):
        seen = {}
        for fate in ("lost_request", "lost_response", "slow"):
            s = PaymentServer()
            seen[fate] = (call(s, 36000, fate), len(s.charges))
        self.assertEqual({v[0] for v in seen.values()}, {("타임아웃", 1000)})      # 손님에겐 같음
        self.assertEqual([v[1] for v in seen.values()], [0, 1, 1])                 # 실제로는 다름

    def test_retry_double_charges_unless_idempotent(self):
        for key, n in ((None, 2), ("pay-7", 1)):
            s = PaymentServer()
            call(s, 36000, "lost_response", key=key)
            call(s, 36000, "ok", key=key)
            self.assertEqual(len(s.charges), n)

    def test_lww_with_skewed_clocks_drops_the_later_write(self):
        early = {"value": "first", "stamp": WallClock(+500).now(1000)}
        late = {"value": "second", "stamp": WallClock(-100).now(1200)}
        self.assertEqual(lww_merge([early, late])["value"], "first")

    def test_monotonic_clock_never_goes_back(self):
        wall, mono = WallClock(), MonotonicClock()
        w0, m0 = wall.now(0), mono.now(0)
        wall.ntp_set(-800)
        self.assertLess(wall.now(200) - w0, 0)
        self.assertEqual(mono.now(200) - m0, 200)

    def test_fencing_token_rejects_stale_lock_holder(self):
        for fencing, final in ((False, "재고 9권"), (True, "재고 4권")):
            lock, db = LockService(lease=10), Storage(fencing)
            t1 = lock.acquire("a", 0)
            self.assertIsNone(lock.acquire("b", 5))                                # 리스 안에서는 못 얻음
            t2 = lock.acquire("b", 10)
            self.assertGreater(t2, t1)
            db.write("재고 4권", t2)
            db.write("재고 9권", t1)
            self.assertEqual(db.value, final)


if __name__ == "__main__":
    unittest.main()
