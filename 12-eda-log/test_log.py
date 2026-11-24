import tempfile
import unittest
from pathlib import Path

import demo
from consumer import left, open_db, take, take_once
from log import Log
from mq import Queue


class QueueTest(unittest.TestCase):
    def test_auto_ack_loses_message_when_consumer_dies(self):
        q = Queue(demo.ORDERS)
        q.receive(auto_ack=True)
        q.consumer_died()
        self.assertEqual([m["id"] for m in q.ready], ["m2", "m3"])

    def test_unacked_message_is_redelivered_first(self):
        q = Queue(demo.ORDERS)
        q.receive(auto_ack=False)
        q.consumer_died()
        self.assertEqual([m["id"] for m in q.ready], ["m1", "m2", "m3"])

    def test_at_least_once_double_counts_without_idempotence(self):
        self.assertEqual(demo.at_least_once(take), (4, 6))

    def test_idempotent_consumer_fixes_duplicate(self):
        self.assertEqual(demo.at_least_once(take_once), (4, 7))

    def test_take_once_skips_same_id(self):
        db = open_db()
        msg = {"id": "x", "book": "DDIA", "qty": 2}
        self.assertEqual((take_once(db, msg), take_once(db, msg), left(db)), (True, False, 8))


class LogTest(unittest.TestCase):
    def test_reading_keeps_lines_and_new_consumer_replays_from_zero(self):
        log = Log(Path(tempfile.mkdtemp()) / "orders.log")
        for e in demo.ORDERS:
            log.append(e)
        for n, _ in log.read("stock"):
            log.commit("stock", n)
        self.assertEqual(log.read("stock"), [])
        self.assertEqual([e["id"] for _, e in log.read("report")], ["m1", "m2", "m3"])
        log.append({"id": "m4", "book": "DDIA", "qty": 1})
        self.assertEqual(log.read("stock"), [(3, {"id": "m4", "book": "DDIA", "qty": 1})])


if __name__ == "__main__":
    unittest.main()
