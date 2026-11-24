import unittest

from answers import ANSWERS
from checklist import CHECKLIST
from scorer import level, risks


class ReviewTest(unittest.TestCase):
    def test_highest_severity_first(self):
        r = risks(CHECKLIST, ANSWERS)
        self.assertEqual(r[0][2], "F1")            # 영향 H × no = 6
        self.assertEqual([x[0] for x in r], sorted((x[0] for x in r), reverse=True))

    def test_yes_is_not_a_risk(self):
        ids = {x[2] for x in risks(CHECKLIST, ANSWERS)}
        self.assertFalse(ids & {"D2", "F2", "S1"})

    def test_missing_answer_counts_as_no(self):
        r1 = [x for x in risks(CHECKLIST, ANSWERS) if x[2] == "R1"][0]
        self.assertEqual((r1[0], r1[5]), (4, "답 없음"))

    def test_levels(self):
        self.assertEqual([level(s) for s in (6, 4, 3, 2, 1)], ["높음", "중간", "중간", "낮음", "낮음"])


if __name__ == "__main__":
    unittest.main()
