"""가장 안쪽 원: 업무 규칙. 이 프로젝트의 무엇도 import하지 않는다."""
from dataclasses import dataclass


class OutOfStock(Exception):
    pass


@dataclass
class Book:
    isbn: str
    title: str
    price: int
    stock: int

    def take(self, qty):
        if qty <= 0 or qty > self.stock:
            raise OutOfStock(self.title)
        self.stock -= qty
        return self.price * qty
