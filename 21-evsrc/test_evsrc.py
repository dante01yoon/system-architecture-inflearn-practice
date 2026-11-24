import unittest

from store import Conflict, EventStore
from stock import load, rebuild, sales_by_day, upcast


class EventSourcingTest(unittest.TestCase):
    def setUp(self):
        self.s = EventStore()
        v = self.s.append("b", 0, "StockReceived", {"qty": 10}, "2026-11-09")
        v = self.s.append("b", v, "BookSold", {"count": 2}, "2026-11-09", schema=1)
        v = self.s.append("b", v, "BookSold", {"qty": 3, "order": "o"}, "2026-11-10")
        self.s.append("b", v, "BookReturned", {"qty": 1}, "2026-11-11")

    def test_rebuild_from_events(self):
        self.assertEqual(rebuild(self.s.read("b")), {"stock": 6, "sold": 4})

    def test_snapshot_gives_same_state_with_fewer_events(self):
        self.s.save_snapshot("b", 3, rebuild(self.s.read("b", until_day="2026-11-10")))
        state, version, n = load(self.s, "b")
        self.assertEqual((state, version, n), ({"stock": 6, "sold": 4}, 3, 1))

    def test_temporal_query(self):
        self.assertEqual(rebuild(self.s.read("b", until_day="2026-11-10"))["stock"], 5)

    def test_upcaster_reads_old_shape_without_rewriting(self):
        self.assertEqual(upcast("BookSold", 1, {"count": 2}), {"qty": 2, "order": None})
        self.assertEqual(self.s.read("b")[1][3], {"count": 2})  # 저장된 건 그대로

    def test_projection(self):
        self.assertEqual(sales_by_day(self.s.read("b")), {"2026-11-09": 2, "2026-11-10": 3})

    def test_stale_writer_is_rejected(self):
        with self.assertRaises(Conflict):
            self.s.append("b", 3, "BookSold", {"qty": 1, "order": "x"}, "2026-11-12")
        self.assertEqual(len(self.s.read("b")), 4)


if __name__ == "__main__":
    unittest.main()
