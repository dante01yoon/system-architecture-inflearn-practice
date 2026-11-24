import unittest

from demo import GANGNAM, seoul
from geo import Index, encode, neighbors
from match import ACCEPT, Store, dispatch, race


class GeoTest(unittest.TestCase):
    def test_known_geohash(self):
        self.assertEqual(encode(57.64911, 10.40744, 11), "u4pruydqqvj")   # 위키백과 예시

    def test_neighbors_are_eight_distinct_cells(self):
        n = neighbors("wydm6d")
        self.assertEqual(len(set(n)), 8)
        self.assertNotIn("wydm6d", n)

    def test_cell_search_matches_brute_force_with_fewer_checks(self):
        idx = seoul()
        idx.checks = 0; a = idx.brute(GANGNAM, 500, 5); full = idx.checks
        idx.checks = 0; b = idx.nearby(GANGNAM, 500, 5)
        self.assertEqual(a, b)
        self.assertLess(idx.checks * 50, full)

    def test_stale_driver_is_skipped(self):
        idx = Index(); idx.update("d", *GANGNAM, now=0)
        self.assertEqual(idx.nearby(GANGNAM, 100, now=31), [])

    def test_move_updates_cell(self):
        idx = Index(); idx.update("d", *GANGNAM, now=0); idx.update("d", 37.56, 126.97, now=1)
        self.assertEqual(idx.nearby(GANGNAM, 100, now=2), [])


class MatchTest(unittest.TestCase):
    cands = [(10, "a"), (20, "b")]

    def test_naive_double_assigns(self):
        got = race(Store(), ["r1", "r2"], self.cands, 0, naive=True)
        self.assertEqual(got["r1"], got["r2"])

    def test_atomic_claim_assigns_once(self):
        got = race(Store(), ["r1", "r2"], self.cands, 0)
        self.assertEqual(sorted(got.values()), ["a", "b"])

    def test_lease_expires_after_accept_window(self):
        st = Store(); dispatch(st, "r1", self.cands, 0)
        self.assertEqual(dispatch(st, "r2", self.cands[:1], ACCEPT - 1), None)
        self.assertEqual(dispatch(st, "r2", self.cands[:1], ACCEPT + 1), "a")


if __name__ == "__main__":
    unittest.main()
