import unittest

from stream import SALES, Consumer, dual_write, open_db, set_status, tumbling


def fresh():
    db = open_db()
    with db:
        db.execute("INSERT INTO orders VALUES (1, 'Clean Architecture', '주문됨')")
    return db


def status(db):
    return db.execute("SELECT status FROM orders WHERE id = 1").fetchone()[0]


class StreamTest(unittest.TestCase):
    def test_dual_write_interleaving_leaves_index_stale(self):
        db, index = fresh(), {1: "주문됨"}
        list(dual_write(db, index, [("A", "db", "결제 완료"), ("B", "db", "취소"), ("B", "index", "취소"), ("A", "index", "결제 완료")]))
        self.assertNotEqual(status(db), index[1])

    def test_cdc_consumer_follows_db_in_order_and_is_idempotent(self):
        db = fresh()
        set_status(db, 1, "결제 완료"); set_status(db, 1, "취소")
        c = Consumer(db); c.poll()
        self.assertEqual(c.view[1], status(db))
        c.offset = 0; c.poll()
        self.assertEqual((c.view[1], c.offset), ("취소", 3))

    def test_consumer_only_reads_new_changes(self):
        db = fresh(); c = Consumer(db); c.poll()
        set_status(db, 1, "결제 완료")
        self.assertEqual(len(c.poll()), 1)

    def test_tumbling_by_event_time_with_grace(self):
        closed, late = tumbling(SALES)
        self.assertEqual([len(w) for _, w, _ in closed], [4, 4, 3])
        self.assertEqual(late, [(58, 130, 35000)])
        self.assertEqual(sum(sum(w) for _, w, _ in closed) + 35000, sum(x[2] for x in SALES))

    def test_no_grace_drops_more(self):
        _, late = tumbling(SALES, grace=0)
        self.assertGreater(len(late), 1)


if __name__ == "__main__":
    unittest.main()
