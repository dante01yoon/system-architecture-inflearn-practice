"""메일: 「주문됨」과 「품절」을 듣고 보낸다."""
from shop_loose import events

outbox = []


def on_order_placed(order):
    outbox.append((order["customer"], f"주문 완료: {order['book']} {order['qty']}권"))


def on_sold_out(book):
    outbox.append(("admin", f"{book} 품절"))


events.subscribe("OrderPlaced", on_order_placed)
events.subscribe("SoldOut", on_sold_out)
