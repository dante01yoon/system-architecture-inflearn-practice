import unittest

from rubric import ITEMS, parse, score, weakest


class RubricTest(unittest.TestCase):
    def test_parse_needs_twelve(self):
        self.assertEqual(ITEMS, 12)
        self.assertEqual(parse("y n, y n y n y n y n y n")[:3], [True, False, True])
        with self.assertRaises(ValueError):
            parse("y n y")

    def test_score_and_tip(self):
        rows = score(parse("nyn ynn nnn ynn"))
        self.assertEqual([r[1] for r in rows], [1, 1, 0, 1])
        self.assertEqual(rows[0][3], "상자를 그리기 전에 누가, 얼마나, 무엇을 묻기")  # 첫 번째로 빠진 문항의 조언
        self.assertEqual(weakest(rows), "기술 깊이")

    def test_full_marks_have_no_tip(self):
        rows = score(parse("y" * 12))
        self.assertTrue(all(r[3] is None for r in rows))


if __name__ == "__main__":
    unittest.main()
