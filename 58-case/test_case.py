import unittest

from demo import race
from storm import lease_storm


class RaceTest(unittest.TestCase):
    def test_stale_plan_plus_cleanup_empties_the_record(self):
        ok, late, n, nxt = race(safe=False)
        self.assertTrue(ok)                        # 시작할 때의 비교는 통과했다
        self.assertEqual(late, "적용")              # 옛 계획이 새 계획을 덮음
        self.assertEqual(n, 0)                     # 빈 레코드
        self.assertEqual(nxt, "기준 계획이 없어 실패")

    def test_check_at_write_time_keeps_addresses(self):
        ok, late, n, nxt = race(safe=True)
        self.assertEqual(late, "거절")
        self.assertEqual(n, 3)
        self.assertEqual(nxt, "적용")


class StormTest(unittest.TestCase):
    def test_retries_without_throttle_collapse(self):
        log = lease_storm()
        self.assertEqual(log[20][0], log[60][0])  # 리스가 더 늘지 않음
        self.assertLess(log[60][0], 600)
        self.assertGreater(log[60][1], log[20][1])  # 줄은 계속 길어짐

    def test_throttle_finishes_without_waste(self):
        log = lease_storm(limit=200)
        self.assertEqual(log[60][0], 600)
        self.assertEqual(log[60][2], 0)


if __name__ == "__main__":
    unittest.main()
