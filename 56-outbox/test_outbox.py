import unittest

from outbox import (Consumer, Crash, PollingRelay, TailingRelay, cancel,
                    cleanup, count, open_db, place, place_naive)


class OutboxTest(unittest.TestCase):
    def test_naive_crash_loses_event(self):
        db, broker = open_db(), []
        with self.assertRaises(Crash):
            place_naive(db, broker, 1, "DDIA", crash=True)
        self.assertEqual((count(db, "SELECT COUNT(*) FROM orders"), broker), (1, []))

    def test_crash_inside_transaction_saves_nothing(self):
        db = open_db()
        with self.assertRaises(Crash):
            place(db, 1, "DDIA", crash="inside")
        self.assertEqual(count(db, "SELECT COUNT(*) FROM orders"), 0)
        self.assertEqual(count(db, "SELECT COUNT(*) FROM outbox"), 0)

    def test_crash_after_commit_is_published_later(self):
        db, broker = open_db(), []
        with self.assertRaises(Crash):
            place(db, 1, "DDIA", crash="after")
        PollingRelay(db, broker).run()
        self.assertEqual([e["id"] for e in broker], ["OrderPlaced#1"])

    def test_relay_crash_duplicates_and_consumer_dedups(self):
        db, broker = open_db(), []
        place(db, 1, "DDIA")
        relay = PollingRelay(db, broker)
        with self.assertRaises(Crash):
            relay.run(crash_after_send=True)
        relay.run()
        self.assertEqual(len(broker), 2)
        c = Consumer()
        self.assertEqual([c.handle(e) for e in broker], ["처리", "중복 무시"])
        self.assertEqual(c.reserved, {"DDIA": 1})

    def test_both_relays_keep_commit_order(self):
        db = open_db()
        place(db, 1, "A"); place(db, 2, "B"); cancel(db, 1)
        a, b = [], []
        PollingRelay(db, a).run(); TailingRelay(db, b).run()
        self.assertEqual(a, b)
        self.assertEqual([e["id"] for e in a], ["OrderPlaced#1", "OrderPlaced#2", "OrderCancelled#1"])
        self.assertEqual(PollingRelay(db, a).run(), 0)

    def test_cleanup_removes_only_published(self):
        db = open_db()
        place(db, 1, "A"); PollingRelay(db, []).run(); place(db, 2, "B")
        self.assertEqual(cleanup(db), 1)
        self.assertEqual(count(db, "SELECT COUNT(*) FROM outbox"), 1)


if __name__ == "__main__":
    unittest.main()
