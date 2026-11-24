import unittest

from incident import minutes
from methods import PAGE, burn, golden, red, use

LOG = minutes()


class CompareTest(unittest.TestCase):
    def test_quiet_before_incident(self):
        for t in range(8):
            self.assertEqual((golden(LOG[t], LOG[0]), red(LOG[t], LOG[0]), use(LOG[t])), ([], {}, {}))
            self.assertLess(burn(LOG, t), 1)

    def test_each_method_names_a_different_thing(self):
        m = LOG[11]
        self.assertEqual(golden(m, LOG[0]), ["지연", "오류", "포화"])      # 증상: 무엇이
        self.assertEqual(red(m, LOG[0]), {"/checkout": "ED"})              # 어느 서비스가
        self.assertEqual(use(m), {"DB 연결 풀": "USE"})                    # 어느 자원이

    def test_traffic_is_unchanged_so_not_flagged(self):
        self.assertNotIn("트래픽", golden(LOG[11], LOG[0]))
        self.assertNotIn("R", red(LOG[11], LOG[0])["/checkout"])

    def test_slo_pages_only_when_users_fail(self):
        first = next(t for t in range(20) if burn(LOG, t) >= PAGE)
        self.assertEqual(first, 11)
        self.assertAlmostEqual(burn(LOG, 11), 30.0)

    def test_burn_is_error_rate_over_budget(self):
        self.assertAlmostEqual(burn(LOG, 9), 0.6 / 5 / 0.1)


if __name__ == "__main__":
    unittest.main()
