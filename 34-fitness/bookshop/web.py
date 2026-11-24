"""가장 위 층: 화면 문구. 주문 층을 부른다."""
from bookshop.orders import place


def render(order):
    return f"주문 완료 {order['total']}원" if order["ok"] else "재고 부족"


def handle(books, isbn, qty):
    return render(place(books, isbn, qty))
