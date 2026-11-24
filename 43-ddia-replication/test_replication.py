import unittest

import quorum
from replica import Follower, Leader
from session import read_your_writes, sticky


class ReplicationTest(unittest.TestCase):
    def test_follower_lags_then_catches_up(self):
        leader = Leader()
        f = Follower("f1", leader, lag=300)
        leader.write("k", "v", now=0)
        self.assertEqual((f.read("k", 50), f.read("k", 300)), (None, "v"))

    def test_read_your_writes_falls_back_to_leader(self):
        leader = Leader()
        f = Follower("f1", leader, lag=300)
        seq = leader.write("k", "mine", now=0)
        self.assertEqual(read_your_writes(seq, leader, [f], "k", 50), ("leader", "mine"))
        self.assertEqual(read_your_writes(seq, leader, [f], "k", 400), ("f1", "mine"))

    def test_sticky_follower_never_goes_back_in_time(self):
        leader = Leader()
        fs = [Follower("f1", leader, lag=100), Follower("f2", leader, lag=900)]
        leader.write("n", 1, now=0)
        f = sticky("minji", fs)
        self.assertIs(f, sticky("minji", fs))
        seen = [f.read("n", t) or 0 for t in range(0, 2000, 50)]
        self.assertEqual(seen, sorted(seen))

    def test_quorum_overlap_only_when_w_plus_r_exceeds_n(self):
        for w, r, stale in ((2, 2, 0), (1, 1, 2), (3, 1, 0)):
            reps = {n: (1, "old") for n in "ABC"}
            quorum.write(reps, "new", 2, to="ABC"[:w])
            self.assertEqual(sum(v[0] < 2 for v in quorum.all_reads(reps, r).values()), stale)


if __name__ == "__main__":
    unittest.main()
