import unittest

from db import build, plan, work
from decide import PROBLEMS, suggest


class IndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = build(20_000)

    def test_scan_then_search(self):
        q = "SELECT * FROM orders WHERE user_id = ?"
        self.assertIn("SCAN", plan(self.db, q, (42,)))
        n0, k0, _ = work(self.db, q, (42,))
        self.db.execute("CREATE INDEX t_user ON orders(user_id)")
        self.assertIn("USING INDEX t_user", plan(self.db, q, (42,)))
        n1, k1, _ = work(self.db, q, (42,))
        self.db.execute("DROP INDEX t_user")
        self.assertEqual(n0, n1)              # 같은 답
        self.assertLess(k1 * 100, k0)         # 일은 훨씬 적게

    def test_left_prefix(self):
        self.db.execute("CREATE INDEX t_ud ON orders(user_id, day)")
        self.assertIn("USING INDEX t_ud", plan(self.db, "SELECT * FROM orders WHERE user_id = 1 AND day >= 9"))
        self.assertIn("SCAN", plan(self.db, "SELECT * FROM orders WHERE day = 9"))
        self.db.execute("DROP INDEX t_ud")

    def test_work_is_repeatable(self):
        q = "SELECT * FROM orders WHERE day = 3"
        self.assertEqual(work(self.db, q)[1], work(self.db, q)[1])


class DecideTest(unittest.TestCase):
    def test_examples(self):
        got = {name: [k for k, _ in suggest(needs)] for name, needs, _ in PROBLEMS}
        self.assertEqual(got["URL 단축기"], ["키-값"])
        self.assertEqual(got["채팅 메시지"], ["와이드 컬럼"])
        self.assertEqual(got["친구 있는 프로필"], ["관계형", "그래프"])
        self.assertEqual(got["상품 검색"], ["관계형", "검색 인덱스"])

    def test_default_is_relational(self):
        self.assertEqual(suggest(set())[0][0], "관계형")


if __name__ == "__main__":
    unittest.main()
