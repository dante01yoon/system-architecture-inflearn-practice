import tempfile
import unittest
from pathlib import Path

from batch import daily_sales, make_logs, make_orders, map_reduce, merge_join, pipeline, sha


class BatchTest(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())

    def test_pipeline_and_mapreduce_agree(self):
        make_logs(self.d / "a.log", n=3000)
        self.assertEqual(map_reduce(self.d / "a.log")[0][:5], pipeline(self.d / "a.log"))

    def test_counts_match_a_plain_count(self):
        make_logs(self.d / "a.log", n=2000)
        paths = [l.split()[3] for l in open(self.d / "a.log")]
        top = pipeline(self.d / "a.log", top=1)[0]
        self.assertEqual(top[0], paths.count(top[1]))

    def test_merge_join_matches_nested_loop(self):
        make_orders(self.d / "orders.tsv", n=500)
        rows = [l.split("\t") for l in open(self.d / "orders.tsv")]
        got = {t: q for t, _, q, _ in merge_join(self.d / "orders.tsv", self.d / "books.tsv", "2026-11-13")}
        for b in open(self.d / "books.tsv"):
            bid, title, _ = b.split("\t")
            want = sum(int(r[2]) for r in rows if r[0] == bid and r[1] == "2026-11-13")
            self.assertEqual(got[title], want)

    def test_rerun_gives_same_file_and_crash_leaves_no_output(self):
        make_orders(self.d / "orders.tsv")
        before = sha(self.d / "orders.tsv")
        first = sha(daily_sales(self.d / "orders.tsv", self.d / "books.tsv", "2026-11-13", self.d))
        (self.d / "sales-2026-11-13.tsv").unlink()
        with self.assertRaises(RuntimeError):
            daily_sales(self.d / "orders.tsv", self.d / "books.tsv", "2026-11-13", self.d, fail_at=3)
        self.assertFalse((self.d / "sales-2026-11-13.tsv").exists())
        self.assertEqual(sha(daily_sales(self.d / "orders.tsv", self.d / "books.tsv", "2026-11-13", self.d)), first)
        self.assertEqual(sha(self.d / "orders.tsv"), before)


if __name__ == "__main__":
    unittest.main()
