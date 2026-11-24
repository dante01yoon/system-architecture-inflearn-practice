"""두 번째 원: 유스케이스. 저장소 약속(Protocol)도 여기, 안쪽이 정한다."""
from dataclasses import dataclass
from typing import Protocol

from bookshop.entities import Book, OutOfStock


@dataclass
class OrderRequest:
    isbn: str
    qty: int


@dataclass
class OrderResult:
    ok: bool
    total: int
    left: int


class BookRepository(Protocol):
    def get(self, isbn: str) -> Book: ...

    def save(self, book: Book) -> None: ...


class PlaceOrder:
    def __init__(self, books: BookRepository):
        self.books = books

    def __call__(self, req: OrderRequest) -> OrderResult:
        book = self.books.get(req.isbn)
        try:
            total = book.take(req.qty)
        except OutOfStock:
            return OrderResult(False, 0, book.stock)
        self.books.save(book)
        return OrderResult(True, total, book.stock)
