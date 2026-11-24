"""세 번째 원: 어댑터. SQLite 표로 같은 BookRepository 약속을 지킨다."""
import sqlite3

from bookshop.entities import Book

COLS = "isbn, title, price, stock"


class SqliteBooks:
    def __init__(self, books, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute(f"CREATE TABLE books ({COLS}, PRIMARY KEY (isbn))")
        rows = [(b.isbn, b.title, b.price, b.stock) for b in books]
        self.db.executemany("INSERT INTO books VALUES (?, ?, ?, ?)", rows)

    def get(self, isbn) -> Book:
        sql = f"SELECT {COLS} FROM books WHERE isbn = ?"
        row = self.db.execute(sql, (isbn,)).fetchone()
        return Book(*row)

    def save(self, book: Book):
        sql = "UPDATE books SET stock = ? WHERE isbn = ?"
        self.db.execute(sql, (book.stock, book.isbn))
        self.db.commit()
