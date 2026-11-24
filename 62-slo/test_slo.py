import unittest

from slo import MIN, alerts, budget, burn, month, sli


class SloTest(unittest.TestCase):
    def test_sli_excludes_client_errors(self):
        rows = [(100, 10, 9)]  # 4xx 10건은 유효 아님
        self.assertEqual(sli(rows), (81, 90))

    def test_burn_rate_one_means_budget_lasts_exactly_the_window(self):
        rows = [(1000, 0, 1)] * 60   # 실패 0.1% = SLO 경계
        self.assertAlmostEqual(burn(rows, 60, 60), 1.0)

    def test_good_month_no_page_and_incident_pages_then_clears(self):
        good = month()
        self.assertEqual(alerts(good), [])
        a, u = budget(good)
        self.assertLess(u, a)
        inc = (16 * MIN + 14 * 60, 25, 0.68)
        bad = month(incident=inc)
        fired = alerts(bad)
        self.assertEqual([on for _, on, _ in fired], [True, False])
        self.assertTrue(inc[0] <= fired[0][0] <= inc[0] + 5)   # 5분 안에 울림
        spent = sum(s for _, _, s in bad[inc[0]:inc[0] + 25]) / budget(bad)[0]
        self.assertAlmostEqual(spent, 0.40, delta=0.02)


if __name__ == "__main__":
    unittest.main()
