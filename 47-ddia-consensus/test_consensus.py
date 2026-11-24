import unittest

from election import Node, elect
from linear import check, op
from twopc import Coordinator, Participant, try_update


class ConsensusTest(unittest.TestCase):
    def test_concurrent_read_may_see_old_value(self):
        h = [op("w", "write", 4, 0, 10), op("r", "read", 5, 5, 12), op("r2", "read", 4, 20, 25)]
        self.assertEqual(check(h, 5), ["r 읽기", "w 쓰기", "r2 읽기"])

    def test_stale_read_after_completed_write_is_not_linearizable(self):
        h = [op("w", "write", 4, 0, 10), op("r2", "read", 5, 20, 25)]
        self.assertIsNone(check(h, 5))

    def test_2pc_participants_block_until_coordinator_recovers(self):
        ps = [Participant("a"), Participant("b")]
        c = Coordinator(ps)
        c.run(crash_after_decision=True)
        self.assertEqual([(p.state, try_update(p)) for p in ps], [("준비됨", "막힘 (잠금)")] * 2)
        c.recover()
        self.assertEqual([(p.state, try_update(p)) for p in ps], [("커밋", "바꿈")] * 2)

    def test_only_majority_side_elects_a_leader(self):
        n = {k: Node(k) for k in "ABCDE"}
        self.assertTrue(elect(n["A"], 2, [n[k] for k in "ABC"], 5)[1])
        for term in (2, 3, 4):
            self.assertFalse(elect(n["D"], term, [n[k] for k in "DE"], 5)[1])

    def test_one_vote_per_term(self):
        n = {k: Node(k) for k in "ABC"}
        self.assertTrue(elect(n["A"], 1, list(n.values()), 3)[1])
        self.assertFalse(elect(n["B"], 1, list(n.values()), 3)[1])      # 같은 임기에 두 번째 리더는 없다


if __name__ == "__main__":
    unittest.main()
