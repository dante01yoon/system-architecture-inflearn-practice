import tempfile
import unittest

from enough import evaluate, load, plan, prioritize, score


def risk(name, kind, l, i, after):
    return {"risk": name, "kind": kind, "likelihood": l, "impact": i, "after": after}


class EnoughTest(unittest.TestCase):
    def test_highest_score_first(self):
        rs = [risk("a", "load", 1, 2, 1), risk("b", "load", 4, 5, 1), risk("c", "load", 3, 3, 1)]
        self.assertEqual([r["risk"] for r in prioritize(rs)], ["b", "c", "a"])

    def test_threshold_is_inclusive(self):
        rs = [risk("six", "decision", 3, 2, 1), risk("four", "load", 2, 2, 1)]
        self.assertEqual([t for _, t in plan(rs)], ["ADR", "그냥 만든다"])

    def test_evaluate_flags_risk_still_above_threshold(self):
        rs = [risk("pay", "load", 4, 5, 2), risk("stock", "unknown", 3, 5, 1), risk("low", "load", 1, 1, 1)]
        self.assertEqual([(r["risk"], b, a, left) for r, b, a, left in evaluate(rs)],
                         [("pay", 20, 10, True), ("stock", 15, 5, False)])

    def test_bookshop_file(self):
        rs = load("risks.csv")
        self.assertEqual(score(prioritize(rs)[0]), 20)
        self.assertEqual(sum(t == "그냥 만든다" for _, t in plan(rs)), 2)

    def test_rejects_out_of_range(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("risk,kind,likelihood,impact,after\nx,load,9,1,1\n")
        with self.assertRaises(ValueError):
            load(f.name)


if __name__ == "__main__":
    unittest.main()
