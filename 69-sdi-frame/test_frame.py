import unittest

from frame import STEPS, timeline, worksheet


class FrameTest(unittest.TestCase):
    def test_minutes_add_up(self):
        for total in (30, 45, 60, 61):
            t = timeline(total)
            self.assertEqual(t[0][1], 0)
            self.assertEqual(t[-1][2], total)
            self.assertTrue(all(a < b for _, a, b in t))           # 걸음마다 1분 이상
            self.assertTrue(all(t[i][2] == t[i + 1][1] for i in range(len(t) - 1)))  # 빈틈 없이 이어짐

    def test_45_matches_weights(self):
        m = {n: b - a for n, a, b in timeline(45)}
        self.assertEqual(m["큰 그림"], 12)
        self.assertEqual(m["핵심 엔티티"], 2)

    def test_too_short(self):
        with self.assertRaises(ValueError):
            timeline(10)

    def test_worksheet_has_all_steps(self):
        md = worksheet("서점 위시리스트")
        self.assertTrue(md.startswith("# 서점 위시리스트"))
        for name, _, _ in STEPS:
            self.assertIn(name, md)


if __name__ == "__main__":
    unittest.main()
