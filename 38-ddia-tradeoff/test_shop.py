import tempfile
import unittest
from pathlib import Path

from shop import build, copy_to_warehouse, report, timed_checkouts, while_reporting


class TradeoffTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = Path(tempfile.mkdtemp())
        cls.orders, cls.warehouse = str(d / "o.db"), str(d / "w.db")
        db = build(cls.orders, n=100_000)
        copy_to_warehouse(db, cls.warehouse).close()
        cls.top = report(db)
        db.close()

    def test_warehouse_is_a_copy_with_same_report(self):
        import sqlite3
        self.assertEqual(report(sqlite3.connect(self.warehouse)), self.top)

    def test_report_on_same_db_slows_checkout_but_warehouse_does_not(self):
        same = while_reporting(self.orders, self.orders, n=80)
        wh = while_reporting(self.warehouse, self.orders, n=80)
        mean = lambda ms: sum(ms) / len(ms)
        self.assertGreater(mean(same), 5 * mean(wh))

    def test_checkouts_land_only_in_operational_db(self):
        import sqlite3
        before = sqlite3.connect(self.warehouse).execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        timed_checkouts(self.orders, n=10)
        self.assertEqual(sqlite3.connect(self.warehouse).execute("SELECT COUNT(*) FROM orders").fetchone()[0], before)


if __name__ == "__main__":
    unittest.main()
