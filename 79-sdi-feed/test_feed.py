import unittest
from array import array

from feed import KEEP, Feed


def tiny():
    """0 = 팔로워 3명(유명인 후보), 1 = 팔로워 2명(2·3)."""
    following = [array("I"), array("I"), array("I", [0, 1]), array("I", [0, 1]), array("I", [0])]
    followers = [array("I", [2, 3, 4]), array("I", [2, 3]), array("I"), array("I"), array("I")]
    return following, followers


class FeedTest(unittest.TestCase):
    def run_posts(self, mode, celeb=None):
        import feed
        old = feed.CELEB
        feed.CELEB = celeb or old
        try:
            f = Feed(*tiny(), mode)
            for i, (a, t) in enumerate([(1, 1.0), (0, 2.0), (1, 3.0)]):
                f.post(a, t, i)
            return f, f.timeline(2)[0]
        finally:
            feed.CELEB = old

    def test_all_modes_give_same_timeline(self):
        want = [(3.0, 2), (2.0, 1), (1.0, 0)]
        for mode in ("push", "pull", "hybrid"):
            _, page = self.run_posts(mode, celeb=3)
            self.assertEqual([(t, p) for t, p, _ in page], want, mode)

    def test_write_and_read_costs(self):
        f, _ = self.run_posts("push");   self.assertEqual((f.writes, f.reads), (3 + 4 + 3, 1))
        f, _ = self.run_posts("pull");   self.assertEqual((f.writes, f.reads), (3, 2))
        f, page = self.run_posts("hybrid", celeb=3)
        self.assertEqual((f.writes, f.reads), (3 + 4, 2))
        self.assertEqual([s for *_, s in page], ["push", "pull", "push"])

    def test_cursor_continues_without_overlap(self):
        f, _ = self.run_posts("push")
        first, cur = f.timeline(2, n=2)
        rest, _ = f.timeline(2, n=2, cursor=cur)
        self.assertEqual([p for _, p, _ in first + rest], [2, 1, 0])

    def test_cache_keeps_latest_only(self):
        f = Feed(*tiny(), "push")
        for i in range(KEEP + 5):
            f.post(1, float(i), i)
        self.assertEqual(len(f.cache[2]), KEEP)
        self.assertEqual(f.cache[2][0][1], 5)


if __name__ == "__main__":
    unittest.main()
