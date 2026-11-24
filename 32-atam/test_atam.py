import unittest

from tree import DECISIONS, TREE, classify, ranked, risks


class Atam(unittest.TestCase):
    def test_hh_first_then_tree_order(self):
        order = [s[2] for s in ranked(TREE)]
        self.assertEqual(order, ["P1", "A1", "M1", "A2", "P2"])

    def test_opposite_directions_make_a_tradeoff(self):
        self.assertEqual(classify({"변경 용이성": +1, "성능": -1}), "트레이드오프")

    def test_same_direction_or_single_is_sensitivity(self):
        self.assertEqual(classify({"성능": +1, "가용성": +1}), "민감 지점")
        self.assertEqual(classify({"가용성": +1}), "민감 지점")

    def test_risks_hurt_hh_scenarios(self):
        self.assertEqual(risks(TREE, DECISIONS), [("쿠폰 규칙을 플러그인으로", "P1", "성능"), ("결제 재시도 다섯 번", "P1", "성능")])


if __name__ == "__main__":
    unittest.main()
