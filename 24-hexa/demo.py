"""같은 육각형(BookShop)을 세 입구로 부른다: CLI · HTTP · 테스트."""
import ast
import json
import threading
import urllib.error
import urllib.request

from adapters import cli, http_api
from adapters.console import ConsoleNotifier
from adapters.fakes import FakePayment, InMemoryBooks, ListNotifier
from adapters.sqlite_repo import SqliteBooks
from shop.core import BookShop
from shop.ports import Book


def wiring(shop):
    return " · ".join(type(p).__name__ for p in (shop.books, shop.payment, shop.notifier))


def post(port, data):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/orders", json.dumps(data).encode(),
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    books = SqliteBooks()
    books.save(Book("B1", "Clean Architecture", 32000, 3))
    shop = BookShop(books, FakePayment(), ConsoleNotifier())

    print("1) 입구: CLI")
    print(f"   출구: {wiring(shop)}")
    cli.run(["B1", "2", "4111-1111"], shop)

    server = http_api.serve(shop)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print("2) 입구: HTTP (같은 육각형, 같은 SQLite)")
    status, body = post(server.server_port, {"isbn": "B1", "qty": 2, "card": "4111-1111"})
    print(f"   HTTP {status}: {body}")
    server.shutdown()

    notes = ListNotifier()
    test = BookShop(InMemoryBooks(Book("B1", "Clean Architecture", 32000, 3)),
                    FakePayment(approve=False), notes)
    print("3) 입구: 테스트 (DB도 카드사도 없이)")
    print(f"   출구: {wiring(test)}")
    r = test.place_order("B1", 1, "4111-1111")
    print(f"   결과: {r.message} · 남은 재고 {r.left} · 보낸 알림 {len(notes.sent)}개")

    tree = ast.parse(open("shop/core.py", encoding="utf-8").read())
    used = sorted({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)})
    print(f"4) shop/core.py가 import하는 것: {', '.join(used)}")


if __name__ == "__main__":
    main()
