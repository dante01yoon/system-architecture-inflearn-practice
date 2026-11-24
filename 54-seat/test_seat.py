import os
import tempfile
import unittest

from seat import buy_locked, buy_naive, buy_unique, buy_version, open_event, pay, race, sweep, view, hold


def tmp():
    return os.path.join(tempfile.mkdtemp(), "t.db")


class RaceTest(unittest.TestCase):
    def test_check_then_write_sells_a_seat_twice(self):
        n, dup, _ = race(tmp(), buy_naive)
        self.assertGreater(dup, 0)

    def test_every_guard_sells_each_seat_once(self):
        for buy in (buy_locked, buy_version, buy_unique):
            n, dup, res = race(tmp(), buy)
            self.assertEqual((n, dup, res["구매"]), (10, 0, 10), buy.__name__)


class HoldTest(unittest.TestCase):
    def setUp(self):
        self.db = open_event(tmp(), ["B-7", "B-8"], unique=True)

    def test_hold_blocks_others_until_expiry(self):
        v1 = hold(self.db, "민지", "B-7", 0)
        self.assertIsNone(hold(self.db, "준호", "B-7", 299))
        self.assertEqual(view(self.db, "B-7", 300), "빈 좌석")             # 줄은 held여도 만료면 빈 좌석
        self.assertEqual(hold(self.db, "준호", "B-7", 300), v1 + 1)

    def test_late_payment_with_old_hold_is_rejected(self):
        v1 = hold(self.db, "민지", "B-7", 0)
        v2 = hold(self.db, "준호", "B-7", 310)
        self.assertTrue(pay(self.db, "민지", "B-7", v1, 320, "k1").startswith("거절"))
        self.assertEqual(pay(self.db, "준호", "B-7", v2, 330, "k2"), "확정")

    def test_payment_after_expiry_is_rejected_even_if_nobody_took_it(self):
        v1 = hold(self.db, "민지", "B-7", 0)
        self.assertTrue(pay(self.db, "민지", "B-7", v1, 300, "k1").startswith("거절"))

    def test_double_click_sells_one_ticket(self):
        v = hold(self.db, "준호", "B-7", 0)
        pay(self.db, "준호", "B-7", v, 10, "k")
        self.assertIn("같은 키", pay(self.db, "준호", "B-7", v, 11, "k"))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0], 1)

    def test_sweeper_frees_only_expired_holds(self):
        hold(self.db, "a", "B-7", 0, ttl=100)
        hold(self.db, "b", "B-8", 0, ttl=500)
        self.assertEqual(sweep(self.db, 200), 1)
        self.assertEqual(view(self.db, "B-8", 200), "선점 중")


if __name__ == "__main__":
    unittest.main()
