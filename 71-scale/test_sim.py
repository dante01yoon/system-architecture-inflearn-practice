import unittest

from sim import STEPS, max_users, per_user


class Scale(unittest.TestCase):
    def test_every_step_supports_more_users(self):
        users = [max_users(c)[0] for _, c in STEPS]
        self.assertEqual(users, sorted(users))
        self.assertLess(users[0], 20_000)
        self.assertGreaterEqual(users[-1], 1_000_000)

    def test_bottleneck_moves(self):
        necks = [max_users(c)[1] for _, c in STEPS]
        self.assertEqual(necks, ['서버 한 대', '앱 서버', 'DB', '읽기 복제본', '앱 서버', '앱 서버', '디스크', '작업자'])

    def test_cache_and_cdn_take_work_off_app(self):
        base = {'split': 1, 'apps': 16}
        app = per_user(base)['앱 서버']
        self.assertLess(per_user(base | {'cache': .8})['앱 서버'], app)
        self.assertLess(per_user(base | {'cdn': 1})['앱 서버'], app)

    def test_queue_moves_heavy_work_to_workers_at_average_rate(self):
        base = {'split': 1, 'apps': 16}
        q = per_user(base | {'queue': 1, 'workers': 1})
        self.assertLess(q['앱 서버'], per_user(base)['앱 서버'])
        self.assertAlmostEqual(q['작업자'] * 3, per_user(base)['앱 서버'] - q['앱 서버'])

    def test_shards_multiply_disk(self):
        self.assertEqual(max_users({'shards': 4})[2]['디스크'], 4 * max_users({})[2]['디스크'])


if __name__ == "__main__":
    unittest.main()
