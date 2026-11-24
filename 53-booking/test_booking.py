import unittest

import booking as b


class BookingTest(unittest.TestCase):
    times = b.arrivals()[:2000]

    def test_arrivals_are_seeded_and_inside_ten_seconds(self):
        self.assertEqual(b.arrivals()[:5], b.arrivals()[:5])
        self.assertTrue(all(0 <= t < b.SECONDS for t in self.times))

    def test_read_check_write_oversells(self):
        path = b.open_db(20)
        b.run_threads(path, self.times, 1, b.naive_read, b.naive_write)
        n, left = b.sold(path)
        self.assertGreater(n, 20)
        self.assertEqual(left, 0)

    def test_conditional_update_sells_exactly_the_seats(self):
        path = b.open_db(20)
        won = b.run_threads(path, self.times, 1, None, lambda db, p, _: b.atomic_reserve(db, p))
        self.assertEqual((won, b.sold(path)), (20, (20, 0)))

    def test_waiting_room_bounds_db_calls_and_keeps_arrival_order(self):
        (n, left), admitted, waits = b.waiting_room(self.times, rate=10, seats=20)
        self.assertEqual((n, left, admitted), (20, 0, 20))
        self.assertLessEqual(max(waits), 20 / 10)
        self.assertEqual(waits, sorted(waits))          # 먼저 온 사람이 먼저 들어간다

    def test_same_idempotency_key_takes_one_seat(self):
        path = b.open_db(5)
        db = b.connect(path)
        self.assertTrue(b.atomic_reserve(db, 1, key="k"))
        self.assertTrue(b.atomic_reserve(db, 1, key="k"))
        self.assertEqual(b.sold(path), (1, 4))


if __name__ == "__main__":
    unittest.main()
