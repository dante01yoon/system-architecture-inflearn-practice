import tempfile
import unittest
from pathlib import Path

from order import OrderService
from stock import Down, StockService

ISBN = "9780134494166"


class DataTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.stock, self.orders = StockService(d / "stock.db"), OrderService(d / "orders.db")
        with self.stock.db:
            self.stock.db.execute("INSERT INTO stock VALUES (?, 5)", (ISBN,))

    def tearDown(self):
        self.stock.db.close(), self.orders.db.close()
        self.tmp.cleanup()

    def test_sync_fails_when_stock_down_and_saves_nothing(self):
        self.stock.up = False
        with self.assertRaises(Down):
            self.orders.place_sync(self.stock, ISBN, 1)
        self.assertEqual(self.orders.db.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)

    def test_async_accepts_while_down_then_catches_up(self):
        self.stock.up = False
        self.orders.place_async(ISBN, 2)
        self.assertEqual((self.orders.relay(self.stock), self.orders.waiting()), (0, 1))
        self.assertEqual(self.stock.left(ISBN), 5)
        self.stock.up = True
        self.assertEqual(self.orders.relay(self.stock), 1)
        self.assertEqual(self.stock.left(ISBN), 3)
        self.assertEqual(self.orders.relay(self.stock), 0)  # 같은 쪽지를 두 번 보내지 않는다

    def test_each_service_has_its_own_tables(self):
        names = lambda db: {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(names(self.orders.db), {"orders", "outbox"})
        self.assertEqual(names(self.stock.db), {"stock"})


if __name__ == "__main__":
    unittest.main()
