import ast
import json
import threading
import unittest
import urllib.error
import urllib.request

from adapters import http_api
from adapters.fakes import FakePayment, InMemoryBooks, ListNotifier
from adapters.sqlite_repo import SqliteBooks
from shop.core import BookShop
from shop.ports import Book


def shop(approve=True, stock=3):
    return BookShop(InMemoryBooks(Book("B1", "Clean Architecture", 32000, stock)), FakePayment(approve), ListNotifier())


class CoreThroughPorts(unittest.TestCase):
    def test_order_charges_saves_and_notifies(self):
        s = shop()
        r = s.place_order("B1", 2, "card")
        self.assertEqual((r.ok, r.left), (True, 1))
        self.assertEqual(s.payment.charged, [64000])
        self.assertEqual(s.books.get("B1").stock, 1)
        self.assertEqual(len(s.notifier.sent), 1)

    def test_declined_payment_keeps_stock_and_sends_nothing(self):
        s = shop(approve=False)
        r = s.place_order("B1", 1, "card")
        self.assertEqual((r.ok, r.message, r.left), (False, "결제 거절", 3))
        self.assertEqual(s.notifier.sent, [])

    def test_out_of_stock_never_charges(self):
        s = shop(stock=1)
        self.assertFalse(s.place_order("B1", 2, "card").ok)
        self.assertFalse(s.place_order("NONE", 1, "card").ok)
        self.assertEqual(s.payment.charged, [])

    def test_sqlite_adapter_keeps_the_same_promise(self):
        books = SqliteBooks()
        books.save(Book("B1", "Clean Architecture", 32000, 3))
        s = BookShop(books, FakePayment(), ListNotifier())
        s.place_order("B1", 2, "card")
        self.assertEqual(books.get("B1").stock, 1)
        self.assertIsNone(books.get("NONE"))

    def test_core_imports_only_ports(self):
        tree = ast.parse(open("shop/core.py", encoding="utf-8").read())
        mods = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        mods |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        self.assertEqual(mods, {"shop.ports"})


class HttpAdapter(unittest.TestCase):
    def setUp(self):
        self.s = shop()
        self.server = http_api.serve(self.s)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def post(self, raw):
        req = urllib.request.Request(f"http://127.0.0.1:{self.server.server_port}/orders", raw)
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_json_order(self):
        status, body = self.post(json.dumps({"isbn": "B1", "qty": 1, "card": "c"}).encode())
        self.assertEqual((status, body["left"]), (200, 2))

    def test_rule_violation_is_409(self):
        status, body = self.post(json.dumps({"isbn": "B1", "qty": 9, "card": "c"}).encode())
        self.assertEqual((status, body["message"]), (409, "재고 부족"))

    def test_bad_json_is_400_and_core_untouched(self):
        status, _ = self.post(b"{not json")
        self.assertEqual(status, 400)
        self.assertEqual(self.s.payment.charged, [])


if __name__ == "__main__":
    unittest.main()
