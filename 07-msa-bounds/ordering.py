"""주문 컨텍스트: 주문 애그리거트. 바깥은 루트(Order)로만 바꾼다."""
from dataclasses import dataclass

MAX_ITEMS = 10


class Rejected(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:
    isbn: str
    title: str
    unit_price: int
    qty: int


class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self._lines = []
        self._discount = 0

    @property
    def lines(self):
        return tuple(self._lines)  # 읽기만: 바깥에 내 목록을 내주지 않는다

    def total(self):
        return sum(x.unit_price * x.qty for x in self._lines) - self._discount

    def add(self, isbn, title, unit_price, qty):
        if qty <= 0:
            raise Rejected("권수는 1 이상")
        if sum(x.qty for x in self._lines) + qty > MAX_ITEMS:
            raise Rejected(f"한 주문은 {MAX_ITEMS}권까지")
        self._lines.append(OrderLine(isbn, title, unit_price, qty))

    def discount(self, amount):
        if self.total() - amount < 0:
            raise Rejected("합계는 0원 이상")
        self._discount += amount
