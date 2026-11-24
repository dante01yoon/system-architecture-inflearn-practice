import unittest
from pathlib import Path

import shop
from saga import Saga

DB = Path(__file__).resolve().parent / "data" / "test.db"


class SagaTest(unittest.TestCase):
    def setUp(self):
        DB.parent.mkdir(exist_ok=True)
        DB.unlink(missing_ok=True)
        self.db = shop.open_db(DB)
        with self.db:
            self.db.execute("INSERT INTO stock VALUES ('DDIA', 1)")

    def tearDown(self):
        self.db.close()
        DB.unlink(missing_ok=True)

    def order(self, qty):
        return {"id": 1, "book": "DDIA", "qty": qty, "price": 30}

    def test_success_runs_every_step(self):
        s = Saga(shop.STEPS)
        self.assertTrue(s.run(self.db, self.order(1)))
        self.assertEqual(s.timeline, ["T1 주문 커밋", "T2 결제 커밋", "T3 재고 커밋", "T4 배송 커밋"])
        self.assertEqual(self.db.execute("SELECT status FROM orders").fetchone()[0], "SHIPPED")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM shipments").fetchone()[0], 1)

    def test_failure_at_step3_compensates_in_reverse(self):
        s = Saga(shop.STEPS)
        self.assertFalse(s.run(self.db, self.order(2)))
        self.assertEqual(s.timeline, ["T1 주문 커밋", "T2 결제 커밋", "T3 재고 실패 (재고 1권)", "C2 결제 보상", "C1 주문 보상"])
        # 보상은 되돌리기(rollback)가 아니라 뜻을 되돌리는 새 쓰기: 행은 남고 상태만 바뀐다
        self.assertEqual(self.db.execute("SELECT status FROM orders").fetchone()[0], "CANCELLED")
        self.assertEqual(self.db.execute("SELECT status FROM payments").fetchone()[0], "REFUNDED")
        self.assertEqual(self.db.execute("SELECT qty FROM stock").fetchone()[0], 1)

    def test_intermediate_state_is_visible_to_others(self):
        view, seen = shop.open_db(DB), []
        Saga(shop.STEPS).run(self.db, self.order(2), watch=lambda: seen.append(
            view.execute("SELECT status FROM payments").fetchone()))
        self.assertEqual(seen[-1], ("PAID",))   # 나중에 환불될 결제가 잠깐 보였다
        view.close()


if __name__ == "__main__":
    unittest.main()
