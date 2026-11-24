import tempfile
import unittest
from pathlib import Path

import adr


class AdrTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "doc/arch"

    def tearDown(self):
        self.tmp.cleanup()

    def test_new_numbers_files_from_nygard_template(self):
        a = adr.new(self.root, "주문 DB는 PostgreSQL을 쓴다")
        b = adr.new(self.root, "결제 결과를 HTTP로 바로 알린다")
        self.assertEqual((a.name, b.name), ("adr-001.md", "adr-002.md"))
        text = a.read_text(encoding="utf-8")
        for head in ("# 1. 주문 DB는 PostgreSQL을 쓴다", "## 상태\n제안됨", "## 맥락", "## 결정", "## 결과"):
            self.assertIn(head, text)

    def test_numbers_are_never_reused(self):
        adr.new(self.root, "a"), adr.new(self.root, "b")
        adr.path(self.root, 1).unlink()
        self.assertEqual(adr.new(self.root, "c").name, "adr-003.md")

    def test_supersede_links_both_ways_and_only_touches_old_status(self):
        adr.new(self.root, "주문 DB는 PostgreSQL을 쓴다")
        old = adr.new(self.root, "결제 결과를 HTTP로 바로 알린다")
        adr.accept(self.root, 2)
        before = old.read_text(encoding="utf-8")
        new = adr.supersede(self.root, 2, "결제 결과를 아웃박스로 발행한다")
        self.assertEqual(adr.status_of(old), "대체됨\n대체한 결정: [3. 결제 결과를 아웃박스로 발행한다](adr-003.md)")
        self.assertEqual(adr.status_of(new), "제안됨\n대체함: [2. 결제 결과를 HTTP로 바로 알린다](adr-002.md)")
        strip = lambda t: adr.STATUS.sub("", t)  # 상태 칸을 빼면 옛 파일은 그대로
        self.assertEqual(strip(old.read_text(encoding="utf-8")), strip(before))

    def test_list_shows_status_and_title(self):
        adr.new(self.root, "주문 DB는 PostgreSQL을 쓴다")
        adr.accept(self.root, 1)
        self.assertEqual(adr.listing(self.root), ["  1  승인됨  주문 DB는 PostgreSQL을 쓴다"])

    def test_supersede_unknown_number_fails(self):
        with self.assertRaises(SystemExit):
            adr.supersede(self.root, 9, "x")


if __name__ == "__main__":
    unittest.main()
