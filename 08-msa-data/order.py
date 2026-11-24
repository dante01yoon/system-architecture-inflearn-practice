"""주문 서비스: 자기 파일 orders.db만 연다. 재고 표는 모른다."""
import json
import sqlite3

from stock import Down

SAVE = "INSERT INTO orders (isbn, qty, status) VALUES (?, ?, ?)"
UNSENT = "SELECT id, body FROM outbox WHERE sent = 0 ORDER BY id"


class OrderService:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, isbn, qty, status)")
        self.db.execute("CREATE TABLE IF NOT EXISTS outbox (id INTEGER PRIMARY KEY, body, sent DEFAULT 0)")

    def place_sync(self, stock, isbn, qty):
        stock.reserve(isbn, qty)  # 재고가 답해야 주문도 끝난다
        with self.db:
            return self.db.execute(SAVE, (isbn, qty, "확정")).lastrowid

    def place_async(self, isbn, qty):
        with self.db:  # 주문과 쪽지를 한 트랜잭션에
            oid = self.db.execute(SAVE, (isbn, qty, "접수")).lastrowid
            note = json.dumps({"order": oid, "isbn": isbn, "qty": qty})
            self.db.execute("INSERT INTO outbox (body) VALUES (?)", (note,))
        return oid

    def relay(self, stock):
        sent = 0
        for row_id, body in self.db.execute(UNSENT).fetchall():
            msg = json.loads(body)
            try:
                stock.reserve(msg["isbn"], msg["qty"])
            except Down:
                break  # 쪽지는 그대로 남는다. 다음에 다시
            with self.db:
                self.db.execute("UPDATE outbox SET sent = 1 WHERE id = ?", (row_id,))
                self.db.execute("UPDATE orders SET status = '확정' WHERE id = ?", (msg["order"],))
            sent += 1
        return sent

    def waiting(self):
        return self.db.execute("SELECT COUNT(*) FROM outbox WHERE sent = 0").fetchone()[0]
