"""포트 = 육각형 가장자리의 약속. 안쪽이 정하고, 바깥 어댑터가 맞춘다."""
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class Book:
    isbn: str
    title: str
    price: int
    stock: int


@dataclass
class OrderResult:
    ok: bool
    message: str
    left: int


# 주도하는 포트(driving): 바깥이 앱을 부르는 입구
class OrderService(Protocol):
    def place_order(self, isbn: str, qty: int, card: str) -> OrderResult: ...


# 주도되는 포트(driven): 앱이 바깥을 부르는 출구
class BookRepository(Protocol):
    def get(self, isbn: str) -> Optional[Book]: ...

    def save(self, book: Book) -> None: ...


class PaymentGateway(Protocol):
    def charge(self, card: str, amount: int) -> bool: ...


class Notifier(Protocol):
    def send(self, text: str) -> None: ...
