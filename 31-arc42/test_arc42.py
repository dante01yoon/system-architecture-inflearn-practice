import tempfile
import unittest
from pathlib import Path

from arc42 import SECTIONS, check, skeleton, split, status

HERE = Path(__file__).parent


class Arc42(unittest.TestCase):
    def test_skeleton_has_twelve_empty_sections(self):
        body = split(skeleton("서점"))
        self.assertEqual(sorted(body), list(range(1, 13)))
        self.assertTrue(all(status(b) == "빈칸" for b in body.values()))

    def test_status(self):
        self.assertEqual(status("\n<!-- 힌트 -->\n"), "빈칸")
        self.assertEqual(status("TODO"), "짧음")
        self.assertEqual(status("로그는 JSON."), "짧음")
        self.assertEqual(status("가" * 40), "채움")

    def test_bookshop_report(self):
        report, links = check(HERE / "bookshop/arc42.md")
        self.assertEqual(len(report), len(SECTIONS))
        st = {n: s for n, _, s in report}
        self.assertEqual([n for n in st if st[n] == "빈칸"], [6, 7, 11, 12])
        self.assertEqual([n for n in st if st[n] == "짧음"], [2, 8])
        self.assertIn(("adr/0004-payment-retry.md", "파일 없음"), links)
        self.assertIn(("adr/0003-coupon-plugin.md", "9장에 없음"), links)

    def test_links_only_from_section_9(self):
        with tempfile.TemporaryDirectory() as d:
            doc = Path(d) / "a.md"
            (Path(d) / "adr").mkdir()
            (Path(d) / "adr/0001-x.md").write_text("x")
            doc.write_text("## 4. 해결 전략\n[ADR](adr/0001-x.md)\n## 9. 아키텍처 결정\n")
            _, links = check(doc)
            self.assertEqual(links, [("adr/0001-x.md", "9장에 없음")])


if __name__ == "__main__":
    unittest.main()
