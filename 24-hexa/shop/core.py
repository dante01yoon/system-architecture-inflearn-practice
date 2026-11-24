"""육각형 안쪽: 주문 규칙. SQLite·HTTP·카드사의 이름은 모르고, 포트만 안다."""
from shop.ports import BookRepository, Notifier, OrderResult, PaymentGateway


class BookShop:
    """주도하는 포트 OrderService를 구현한다."""

    def __init__(self, books: BookRepository, payment: PaymentGateway, notifier: Notifier):
        self.books, self.payment, self.notifier = books, payment, notifier

    def place_order(self, isbn: str, qty: int, card: str) -> OrderResult:
        book = self.books.get(isbn)
        if book is None or qty <= 0 or qty > book.stock:
            return OrderResult(False, "재고 부족", book.stock if book else 0)
        if not self.payment.charge(card, book.price * qty):
            return OrderResult(False, "결제 거절", book.stock)
        book.stock -= qty
        self.books.save(book)
        self.notifier.send(f"{book.title} {qty}권 주문 완료")
        return OrderResult(True, f"{book.price * qty:,}원 결제", book.stock)
