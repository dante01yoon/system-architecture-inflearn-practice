import unittest

from calc import RTT, availability, downtime_hours, machines, nearest, page_wait


class Calc(unittest.TestCase):
    def test_machines_round_up_with_headroom(self):
        self.assertEqual(machines(20_000, 2_000, 0), 10)
        self.assertEqual(machines(20_000, 2_000), 15)       # 20,000 / 1,400 = 14.3 → 15

    def test_more_copies_less_downtime(self):
        one, two, three = (availability(0.995, n) for n in (1, 2, 3))
        self.assertAlmostEqual(one, 0.995)
        self.assertAlmostEqual(two, 1 - 0.005 ** 2)
        self.assertLess(downtime_hours(three), downtime_hours(two))
        self.assertLess(downtime_hours(two), downtime_hours(one))
        self.assertAlmostEqual(downtime_hours(one), 43.8)

    def test_nearest_region_is_own_region(self):
        for user in RTT:
            self.assertEqual(nearest(user), user)
            self.assertLessEqual(page_wait(user, nearest(user)), page_wait(user, '서울'))


if __name__ == "__main__":
    unittest.main()
