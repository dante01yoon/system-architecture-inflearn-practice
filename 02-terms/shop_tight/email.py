"""메일: 영수증 문구를 만들려고 주문 모듈을 직접 부른다."""
from shop_tight import orders

outbox = []


def send_receipt(order):
    outbox.append((order["customer"], f"주문 완료: {orders.format_order(order)}"))


def send_admin(text):
    outbox.append(("admin", text))
