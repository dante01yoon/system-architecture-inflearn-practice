import unittest

from sim import MAX_CONN, run


class Traffic(unittest.TestCase):
    def test_same_input_same_result(self):
        self.assertEqual(run(), run())

    def test_spike_piles_up_at_db_not_app(self):
        r = run()
        self.assertGreater(r['db_use'], 1.0)
        self.assertLess(r['app_use'], 0.5)
        self.assertGreater(r['db_wait'], 5000)
        self.assertEqual(r['app_wait'], 0)

    def test_more_app_servers_do_not_fix_db_and_break_pool(self):
        r = run(servers=8)
        self.assertGreater(r['db_use'], 1.0)          # 아직 DB가 넘침
        self.assertGreater(r['errors'], 0)            # 8대 × 15 = 120 > 100
        self.assertGreater(8 * 15, MAX_CONN)

    def test_cache_cuts_db_work_about_80_percent(self):
        cut = 1 - run(servers=8, pool=12, hit=0.9)['db_use'] / run()['db_use']
        self.assertGreater(cut, 0.75)

    def test_pool_within_limit_has_no_errors(self):
        r = run(servers=8, pool=12, hit=0.9)
        self.assertEqual(r['errors'], 0)
        self.assertLess(r['p95'], 20)


if __name__ == "__main__":
    unittest.main()
