import unittest
from pathlib import Path

from checker import check, flags, parse

T = Path(__file__).parent / "transcripts"


class CheckerTest(unittest.TestCase):
    def test_parse_skips_untimed_lines(self):
        rows = parse("# 제목\n[01:30] 나: 몇 명인가요?\n[02:00] # 큰 그림")
        self.assertEqual(rows, [(1.5, "나", "몇 명인가요?"), (2.0, "#", "큰 그림")])

    def test_questions_only_count_in_requirements(self):
        r = check("[00:00] # 요구\n[00:10] 나: 몇 명?\n[01:00] # 큰 그림\n[02:00] 나: 캐시는?")
        self.assertEqual(r["요구 질문"], 1)

    def test_interviewer_words_do_not_count(self):
        r = check("[00:00] # 요구\n[00:10] 면접관: 초당 100번이고 비용은 대신 장애 나면?")
        self.assertEqual((r["숫자"], r["트레이드오프"], r["장애 대비"]), (0, 0, 0))

    def test_weak_fails_everything(self):
        r = check((T / "weak.txt").read_text(encoding="utf-8"))
        self.assertEqual(len(flags(r)), 6)
        self.assertEqual(r["phases"]["큰 그림"], 40)

    def test_better_passes(self):
        r = check((T / "better.txt").read_text(encoding="utf-8"))
        self.assertEqual(flags(r), [])
        self.assertEqual(sum(r["phases"].values()), 45)


if __name__ == "__main__":
    unittest.main()
