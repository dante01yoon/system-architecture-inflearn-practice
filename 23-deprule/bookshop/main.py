"""가장 바깥 원: 부품을 골라 끼운다. 모든 원을 알아도 되는 곳."""
from bookshop.adapters.memory_repo import MemoryBooks
from bookshop.adapters.sqlite_repo import SqliteBooks
from bookshop.entities import Book
from bookshop.usecases import PlaceOrder

BOOKS = [Book("9780134494166", "Clean Architecture", 32000, 3)]
REPOS = {"memory": MemoryBooks, "sqlite": SqliteBooks}


def build(kind):
    return PlaceOrder(REPOS[kind](BOOKS))
