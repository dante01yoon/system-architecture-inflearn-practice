"""컨텍스트 사이의 번역: 한쪽 모델을 다른 쪽 말로 옮긴다."""
from catalog import Book
from ordering import Order
from shipping import WEIGHT_G, Parcel


def add_to_order(order: Order, book: Book, qty):
    order.add(book.isbn, book.title, book.price, qty)  # 카탈로그 책 -> 주문 줄


def to_parcels(order: Order):
    return [Parcel(x.isbn, WEIGHT_G[x.isbn], x.qty) for x in order.lines]  # 주문 줄 -> 배송 상자
