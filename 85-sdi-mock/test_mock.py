import unittest
from collections import Counter

from sketch import CountMin
from stream import purchases
from topk import Leaderboard, Window, exact_top


class WindowTest(unittest.TestCase):
    def test_old_minutes_fall_out(self):
        w = Window(minutes=2)
        for t in (0, 60, 120):           # 0분 · 1분 · 2분에 한 번씩
            w.add(t, "a")
        self.assertEqual(w.counts(now=180)["a"], 2)   # 1분 · 2분만 남는다
        self.assertEqual(w.counts(now=240)["a"], 1)


class LeaderboardTest(unittest.TestCase):
    def setUp(self):
        self.events = purchases(n=20_000)

    def test_merge_equals_exact(self):
        for hot in ((), ("책99999", "책00001")):
            board = Leaderboard(4, hot)
            for t, b in self.events:
                board.add(t, b)
            self.assertEqual(board.top(5, 5400), exact_top(self.events, 5, 5400))

    def test_hot_book_spreads_writes(self):
        plain, spread = Leaderboard(4), Leaderboard(4, ("책99999", "책00001"))
        for t, b in self.events:
            plain.add(t, b)
            spread.add(t, b)
        self.assertLess(max(spread.writes), max(plain.writes))
        self.assertEqual(sum(spread.writes), len(self.events))


class CountMinTest(unittest.TestCase):
    def test_never_undercounts(self):
        events = purchases(n=20_000)
        exact = Counter(b for _, b in events)
        cms = CountMin(500, 4)
        for _, b in events:
            cms.add(b)
        self.assertTrue(all(cms.query(b) >= n for b, n in exact.items()))
        self.assertEqual(cms.query("없는 책") >= 0, True)


if __name__ == "__main__":
    unittest.main()
