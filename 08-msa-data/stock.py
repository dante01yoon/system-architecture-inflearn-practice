"""재고 서비스: 자기 파일 stock.db만 연다."""
import sqlite3


class Down(Exception):
    pass


class StockService:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS stock (isbn TEXT PRIMARY KEY, qty INT)")
        self.up = True

    def reserve(self, isbn, qty):
        if not self.up:
            raise Down("재고 서비스 응답 없음")
        with self.db:
            self.db.execute("UPDATE stock SET qty = qty - ? WHERE isbn = ?", (qty, isbn))

    def left(self, isbn):
        return self.db.execute("SELECT qty FROM stock WHERE isbn = ?", (isbn,)).fetchone()[0]
