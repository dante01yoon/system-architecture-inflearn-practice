"""주도하는 어댑터 ①: 명령줄 → OrderService."""
from shop.ports import OrderService


def run(argv, service: OrderService):
    isbn, qty, card = argv
    r = service.place_order(isbn, int(qty), card)
    print(f"   CLI 응답: {'성공' if r.ok else '실패'} · {r.message} · 남은 재고 {r.left}")
