import random
import unittest

from shard import by_hash, by_range, count, moved_fixed, moved_mod_n, orders, range_bounds, salted, today_orders


class ShardTest(unittest.TestCase):
    def setUp(self):
        self.old = orders()
        self.keys = [o[0] for o in self.old]

    def test_range_puts_all_new_dates_on_last_shard(self):
        bounds = range_bounds([f"{o[1]}/{o[0]}" for o in self.old], 4)
        c = count([by_range(f"{o[1]}/{o[0]}", bounds) for o in today_orders()], 4)
        self.assertEqual(c, [0, 0, 0, 1000])

    def test_hash_spreads_new_orders(self):
        c = count([by_hash(o[0], 4) for o in today_orders()], 4)
        self.assertTrue(all(200 < x < 300 for x in c), c)

    def test_mod_n_moves_most_keys_fixed_partitions_move_about_one_fifth(self):
        self.assertGreater(moved_mod_n(self.keys, 4, 5), 0.75)
        frac, parts = moved_fixed(self.keys, 64, 4, 5)
        self.assertEqual(parts, 12)
        self.assertAlmostEqual(frac, 0.2, delta=0.03)

    def test_salting_uses_every_shard(self):
        rnd = random.Random(3)
        c = count([by_hash(salted("작가007", rnd), 4) for _ in range(10_000)], 4)
        self.assertTrue(all(x > 1000 for x in c), c)


if __name__ == "__main__":
    unittest.main()
