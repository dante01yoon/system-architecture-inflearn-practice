"""주도되는 어댑터: SQLite 저장소. BookRepository 약속에 맞춘다."""
import sqlite3

from shop.ports import Book


class SqliteBooks:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)  # HTTP 스레드에서도 부른다
        self.db.execute("CREATE TABLE IF NOT EXISTS books"
                        " (isbn TEXT PRIMARY KEY, title TEXT, price INT, stock INT)")

    def get(self, isbn):
        row = self.db.execute("SELECT isbn, title, price, stock FROM books WHERE isbn = ?",
                              (isbn,)).fetchone()
        return Book(*row) if row else None

    def save(self, book):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO books VALUES (?, ?, ?, ?)",
                            (book.isbn, book.title, book.price, book.stock))
