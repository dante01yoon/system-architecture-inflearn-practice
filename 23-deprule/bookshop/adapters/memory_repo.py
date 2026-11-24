"""세 번째 원: 어댑터. 메모리 사전으로 BookRepository 약속을 지킨다."""
from dataclasses import replace

from bookshop.entities import Book


class MemoryBooks:
    def __init__(self, books):
        self.rows = {b.isbn: replace(b) for b in books}

    def get(self, isbn) -> Book:
        return replace(self.rows[isbn])

    def save(self, book: Book):
        self.rows[book.isbn] = replace(book)
